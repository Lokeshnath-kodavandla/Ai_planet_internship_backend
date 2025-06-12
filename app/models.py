from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Model used for storing and retrieving PDF document metadata
class PDFDocument(BaseModel):
    id: Optional[int] = None
    filename: str
    file_path: str
    upload_date: str
    file_size: int
    extracted_text: str
    created_at: Optional[str] = None


# Response returned after uploading a PDF
class PDFUploadResponse(BaseModel):
    success: bool
    message: str
    pdf_id: Optional[int] = None
    filename: Optional[str] = None
    text_preview: Optional[str] = None


# Response returned after asking a question
class QuestionAnswerResponse(BaseModel):
    success: bool
    question: str
    answer: str
    pdf_filename: str
    confidence: Optional[float] = None  # Not used now, but useful later
