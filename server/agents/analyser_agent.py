from __future__ import annotations
from typing import List, Dict, Any
from server.agents.base_agent import BaseAgent
import yaml
import os

RULEBOOK_PATH = os.path.join(os.path.dirname(__file__), "rules", "rulebook.yaml")


class AnalyserAgent(BaseAgent):
    """
    Analyses tenancy agreement clauses using rulebook and outputs structured risk analysis.
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
        issues = []
        for clause in clauses:
            issue = self._analyze_clause(clause)
            issues.append(issue)

        summary = {
            "high_risk": sum(1 for i in issues if i["risk"] == "HIGH"),
            "medium_risk": sum(1 for i in issues if i["risk"] == "MEDIUM"),
            "ok": sum(1 for i in issues if i["risk"] == "OK"),
            "total": len(issues),
        }

        buckets = ["Unfair Clauses", "Stamp Duty", "Your Rights"]

        return {"summary": summary, "issues": issues, "buckets": buckets}

    def _extract_clauses(self, intake_json: Dict[str, Any]) -> List[str]:
        return intake_json.get("clauses", [])

    def _analyze_clause(self, clause: str) -> Dict[str, Any]:
        matched_rule = None
        for rule in self.rules:
            if (
                rule["id"].replace("_", " ") in clause.lower()
                or rule["category"].lower() in clause.lower()
            ):
                matched_rule = rule
                break
            desc_keywords = rule["description"].lower().split()
            if any(word in clause.lower() for word in desc_keywords[:3]):
                matched_rule = rule
                break

        if matched_rule:
            risk = matched_rule["risk"]
            category = matched_rule["category"]
            rationale = matched_rule["rationale"] + " (Singapore context)"
            recommendation = matched_rule["recommendation"]
            reference = str(matched_rule["reference"])
        else:
            risk = "OK"
            category = "Your Rights"
            rationale = "Clause does not match any known high-risk or unfair patterns. (Singapore context)"
            recommendation = "No action needed."
            reference = "CEA template"

        return {
            "clause": clause if clause else "[Missing clause]",
            "risk": risk,
            "category": category,
            "rationale": rationale,
            "recommendation": recommendation,
            "reference": reference,
        }
