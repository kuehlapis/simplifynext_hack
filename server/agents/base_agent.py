from pydantic import BaseModel, Field
from google import genai
from server.util.config import GEMINI_API_KEY, MODEL_NAME


class BaseAgent(BaseModel):
    model: str = Field(default=MODEL_NAME)
    client: genai.Client = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            raise ValueError(f"Failed to initialize BaseAgent: {e}")
