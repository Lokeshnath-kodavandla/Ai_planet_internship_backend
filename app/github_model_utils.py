# app/github_model_utils.py

import os
from dotenv import load_dotenv
import httpx

load_dotenv()

GITHUB_API_URL = "https://openrouter.ai/api/v1/chat/completions"
GITHUB_MODEL = os.getenv("GITHUB_MODEL_NAME")
GITHUB_TOKEN = os.getenv("GITHUB_MODEL_TOKEN")

def github_model_answer(question: str, document_text: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": GITHUB_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant for answering questions from PDF documents."},
                {"role": "user", "content": f"Context:\n{document_text}\n\nQuestion:\n{question}"}
            ]
        }

        response = httpx.post(GITHUB_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        return data['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"GITHUB MODEL ERROR: {str(e)}"
