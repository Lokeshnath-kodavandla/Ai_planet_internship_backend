from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.utils import extract_text_from_pdf, llm_question_answering
from typing import List
import os
import sqlite3
from datetime import datetime
import fitz  # PyMuPDF
import hashlib
from pathlib import Path

# Import local utilities
from app.database import get_db, init_db
from app.models import PDFDocument

# Create FastAPI instance
app = FastAPI(
    title="PDF Question Answering API",
    description="Upload PDFs and ask questions about their content",
    version="1.0.0"
)

# Allow requests from all domains (for dev only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    init_db()

# ===========================
# Pydantic Models
# ===========================

class QuestionRequest(BaseModel):
    pdf_id: int
    question: str

class QuestionResponse(BaseModel):
    answer: str
    pdf_filename: str

class PDFResponse(BaseModel):
    id: int
    filename: str
    upload_date: str
    file_size: int
    text_preview: str

# ===========================
# API Routes
# ===========================

@app.get("/")
def root():
    return {
        "message": "PDF Question Answering API",
        "endpoints": {
            "upload": "POST /upload-pdf",
            "ask": "POST /ask-question",
            "list": "GET /pdfs",
            "delete": "DELETE /pdfs/{id}"
        }
    }

@app.post("/upload-pdf", response_model=PDFResponse)
async def upload_pdf(file: UploadFile = File(...), db: sqlite3.Connection = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    file_content = await file.read()

    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    file_hash = hashlib.md5(file_content).hexdigest()[:8]
    safe_filename = f"{file_hash}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as f:
        f.write(file_content)

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="No extractable text found in PDF")

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO pdf_documents (filename, file_path, upload_date, file_size, extracted_text)
        VALUES (?, ?, ?, ?, ?)
    """, (
        file.filename,
        str(file_path),
        datetime.now().isoformat(),
        len(file_content),
        text
    ))
    db.commit()

    pdf_id = cursor.lastrowid
    preview = text[:200] + "..." if len(text) > 200 else text

    return PDFResponse(
        id=pdf_id,
        filename=file.filename,
        upload_date=datetime.now().isoformat(),
        file_size=len(file_content),
        text_preview=preview
    )

@app.post("/ask-question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT filename, extracted_text FROM pdf_documents WHERE id = ?", (request.pdf_id,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="PDF not found")

    filename, extracted_text = result
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text content available for this PDF")

    # Using LLM to answer the question
    answer = llm_question_answering(request.question, extracted_text)

    return QuestionResponse(answer=answer, pdf_filename=filename)

@app.get("/pdfs", response_model=List[PDFResponse])
def list_pdfs(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id, filename, upload_date, file_size, extracted_text FROM pdf_documents ORDER BY upload_date DESC")
    rows = cursor.fetchall()

    results = []
    for row in rows:
        preview = row[4][:200] + "..." if len(row[4]) > 200 else row[4]
        results.append(PDFResponse(
            id=row[0],
            filename=row[1],
            upload_date=row[2],
            file_size=row[3],
            text_preview=preview
        ))
    return results

@app.delete("/pdfs/{pdf_id}")
def delete_pdf(pdf_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT file_path FROM pdf_documents WHERE id = ?", (pdf_id,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="PDF not found")

    file_path = Path(result[0])
    cursor.execute("DELETE FROM pdf_documents WHERE id = ?", (pdf_id,))
    db.commit()

    if file_path.exists():
        os.remove(file_path)

    return {"message": "PDF deleted successfully"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render sets PORT env var
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
