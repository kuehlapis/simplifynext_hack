from google import genai
from server.util.intake_config import GEMINI_API_KEY, MODEL_NAME


class BaseAgent:
    def __init__(self):
        self.model = MODEL_NAME
        self.client = genai.Client(api_key=GEMINI_API_KEY)
