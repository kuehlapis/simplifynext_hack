from __future__ import annotations
from typing import List, Dict, Any
from server.agents.base_agent import BaseAgent
import yaml
import os
import json

from server.agents.schema import AnalysisResult

RULEBOOK_PATH = os.path.join(os.path.dirname(__file__), "rules", "rulebook.yaml")


class AnalyserAgent(BaseAgent):
    """
    Analyses tenancy agreement clauses using rulebook and outputs structured risk analysis.
    Uses LangChain for LLM-based analysis.
    """

    def __init__(self):
        super().__init__()
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        with open(RULEBOOK_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("rules", [])

    def analyze(self, intake_json: Dict[str, Any]) -> Dict[str, Any]:
        clauses = self._extract_clauses(intake_json)
        rulebook_text = yaml.dump({"rules": self.rules}, allow_unicode=True)
        system_prompt = self.get_system_prompt("analyser_agent")
        input_text = f"Rulebook YAML:\n{rulebook_text}\n\nClauses:\n{clauses}\n\nOutput JSON as specified."
        try:
            result: AnalysisResult = self.run(system_prompt, input_text, AnalysisResult)

            # delete later
            with open(
                "./agents/outputs/analysis_result.json", "w", encoding="utf-8"
            ) as f:
                json.dump(result.dict(), f, ensure_ascii=False, indent=2)

            print("Saved JSON to analysis_result.json")
            return result.model_dump()
        except Exception as e:
            raise RuntimeError(f"Analysis failed: {e}")

    def _extract_clauses(self, intake_json: Dict[str, Any]) -> List[str]:
        return intake_json.get("clauses", [])
