from server.agents.base_agent import BaseAgent
from server.util.intake_config import INTAKE_PROMPT
from google.genai import types
import json
import hashlib
import re


class IntakeAgent(BaseAgent):
    def __init__(self, document: str):
        super().__init__()
        self.document = document
        self.memory = {}

    def text_normalization(self):
        # system_instructions = """
        #     You are a text normalizing assistant.
        #     Your task is to normalize text formatting, fix spacing issues, and standardize OCR output.
        #     Anchor the output and persist in JSON format.
        #     Don't include signature areas.
        # """
        print("Cleaning up your lease...")
        try:
            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(system_instruction=INTAKE_PROMPT),
                contents=self.document,
            )

            match = re.search(r"\{.*\}", response.text, flags=re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in AI output")
            json_str = match.group(0)

            json_str = json_str.replace("\\n", "\n")

            data = json.loads(json_str, strict=False)

            anchor_id = hashlib.md5(json_str.encode()).hexdigest()
            self.memory["anchor"] = {"id": anchor_id, "content": data}

            with open("intake_agent.json", "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)

            print("Saved JSON to intake_agent.json")

            return response.text

        except Exception as e:
            raise ValueError(f"Error during text normalization: {e}")
