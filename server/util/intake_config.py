from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
INTAKE_PROMPT = "You are a text normalizing assistant. Your task is to normalize text formatting, fix spacing issues, and standardize OCR output. Anchor the output and persist in JSON format. Don't include signature areas."
