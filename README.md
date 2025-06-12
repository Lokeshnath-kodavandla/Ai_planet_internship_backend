# 🧠 AI Planet Internship Assessment Task.

This backend service allows users to upload PDF documents and ask natural language questions about their contents. It uses **FastAPI** for the API, **PyMuPDF** for PDF parsing, **SQLite** for storage, and **LangChain + OpenRouter** for LLM-based answers.

---

## 🔧 Tech Stack

- **Backend Framework:** FastAPI
- **PDF Parsing:** PyMuPDF (`fitz`)
- **LLM Integration:** LangChain + OpenRouter
- **Database:** SQLite
- **Environment Management:** `python-dotenv`
- **Deployment Ready:** Works locally and on Render

---

## 📦 Features

- Upload PDFs and extract readable text
- Store documents and metadata in SQLite
- Ask questions about uploaded PDFs using LLMs
- Clean and structured API routes
- CORS enabled for frontend use

---

## 📁 Project Structure

.
├── app/
│ ├── main.py # FastAPI app and routes
│ ├── utils.py # PDF extraction + LLM logic
│ ├── database.py # SQLite setup
│ ├── models.py # DB schema models
├── uploads/ # Saved PDFs
├── .env # API Keys and configs
├── requirements.txt # Python dependencies
├── pdf_qa.db # SQLite database (auto-created)




## 🔄 API Endpoints

### POST `/upload-pdf`
- Validates PDF file
- Extracts text using PyMuPDF
- Stores metadata and extracted text in SQLite DB
- Returns `pdf_id` and filename

### POST `/ask-question`
- Receives `pdf_id` and user question
- Retrieves text from database
- Sends to LLM for generating an answer
- Returns the answer

### GET `/pdfs` *(optional)*
- Lists all uploaded PDFs

### DELETE `/pdfs/{id}` *(optional)*
- Deletes PDF and related data from storage and DB

## 🧠 Core Logic

### extract_text_from_pdf(path)
- Uses `fitz` (PyMuPDF) to get text from all pages

### llm_question_answering(question, text)
- Sends data to OpenRouter API
- Returns a concise answer based on the prompt

## 🗄️ Database Schema

**Table: `pdf_documents`**


id INTEGER PRIMARY KEY,
filename TEXT,
file_path TEXT,
upload_date TEXT,
file_size INTEGER,
extracted_text TEXT



## ❗ Error Handling
- Invalid or non-PDF uploads
- PDFs with no extractable text
- Questions sent without uploading PDF
- Proper HTTP exceptions and fallback messages included

## 🔮 Future Enhancements
- Authentication (Login system)
- Multi-PDF context support
- Advanced error logging
- Document preview integration

---
