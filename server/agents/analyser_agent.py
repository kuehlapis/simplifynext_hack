from __future__ import annotations
from typing import List, Dict, Any
from server.agents.base_agent import BaseAgent
import yaml
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser

RULEBOOK_PATH = os.path.join(os.path.dirname(__file__), "rules", "rulebook.yaml")


class AnalyserAgent(BaseAgent):
    """
    Analyses tenancy agreement clauses using rulebook and outputs structured risk analysis.
    Now uses LangChain for LLM-based analysis.
    """

    def __init__(self):
        super().__init__()
        self.rules = self._load_rules()
        self.llm = ChatGoogleGenerativeAI(
            model=self.model, google_api_key=self.client.api_key
        )
        self.parser = JsonOutputParser()

    def _load_rules(self) -> List[Dict[str, Any]]:
        with open(RULEBOOK_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("rules", [])

    def analyze(self, intake_json: Dict[str, Any]) -> Dict[str, Any]:
        clauses = self._extract_clauses(intake_json)
        rulebook_text = yaml.dump({"rules": self.rules}, allow_unicode=True)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a tenancy agreement analysis assistant for Singapore. "
                    "Given a list of clauses and a YAML rulebook, output a JSON object with: "
                    "1. summary (counts of high_risk, medium_risk, ok, total), "
                    "2. issues (list of dicts with clause, risk, category, rationale, recommendation, reference), "
                    "3. buckets (unique categories found). "
                    "Always cite the rulebook and use Singapore context.",
                ),
                (
                    "human",
                    "Rulebook YAML:\n{rulebook}\n\nClauses:\n{clauses}\n\nOutput JSON as specified.",
                ),
            ]
        )
        chain = prompt | self.llm | self.parser

        try:
            result = chain.invoke({"rulebook": rulebook_text, "clauses": clauses})
            return result
        except Exception as e:
            raise RuntimeError(f"LangChain analysis failed: {e}")

    def _extract_clauses(self, intake_json: Dict[str, Any]) -> List[str]:
        return
