import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # Load your GEMINI_API_KEY from .env

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

response = genai.GenerativeModel("gemini-pro").generate_content("What is Generative AI?")
print(response.text)
