import fitz  # PyMuPDF
import re
from pathlib import Path
from dotenv import load_dotenv
import os

from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
print("✅ Loaded OPENROUTER_API_KEY:", api_key is not None)

def extract_text_from_pdf(file_path: Path) -> str:
    try:
        doc = fitz.open(str(file_path))
        text_content = [page.get_text() for page in doc if page.get_text().strip()]
        doc.close()
        return "\n\n".join(text_content)
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def llm_question_answering(question: str, document_text: str) -> str:
    try:
        llm = ChatOpenAI(
            temperature=0,
            model_name="mistralai/mistral-7b-instruct",  # OR "gpt-3.5-turbo", "meta-llama/llama-3-8b-instruct"
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        chain = load_qa_chain(llm, chain_type="stuff")
        docs = [Document(page_content=document_text)]
        result = chain.run(input_documents=docs, question=question)
        return result.strip()
    except Exception as e:
        return f"GITHUB MODEL ERROR: {str(e)}"
