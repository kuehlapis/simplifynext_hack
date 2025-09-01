import hashlib
import json
from server.agents.base_agent import BaseAgent
from server.agents.schema import IntakeAgentOutput
from datetime import date


class IntakeAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.memory = {}

    def normalization(self, document: str):
        print("Cleaning up your lease...")

        system_prompt = self.get_system_prompt("intake_agent")

        try:
            response: IntakeAgentOutput = self.run(
                system_prompt, document, IntakeAgentOutput
            )

            anchor_id = hashlib.md5(
                json.dumps(response.model_dump(), ensure_ascii=False).encode()
            ).hexdigest()

            if response.date or response.date.strip() == "":
                response.date = date.today().isoformat()

            self.memory["summary"] = {"id": anchor_id, "content": response.model_dump()}

            with open(
                "server/agents/outputs/intake_agent.json", "w", encoding="utf-8"
            ) as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)

            print("Saved JSON to intake_agent.json")

            return response.model_dump()

        except Exception as e:
            raise ValueError(f"Error during text normalization: {e}")
