import os
import re
import yaml
from typing import List, Callable
from functools import partial

GR_RULEBOOK = os.path.join(os.path.dirname(__file__), "rules", "guardrail.yaml")


class GuardrailAgent:
    def __init__(self):
        self.rules: List[Callable[[str], str]] = []
        self._load_rules()

    def _load_rules(self):
        with open(GR_RULEBOOK, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for rule in data.get("rules", []):
            if rule["type"] == "regex":
                pattern = rule["pattern"]
                response = rule["response"]
                self.rules.append(
                    partial(self._apply_regex, pattern=pattern, response=response)
                )

            elif rule["type"] == "append":
                response = rule["response"]
                self.rules.append(partial(self._apply_append, response=response))

            elif rule["type"] == "protect":
                keywords = [kw.lower() for kw in rule.get("pattern", [])]
                response = rule["response"]
                self.rules.append(
                    partial(self._apply_protect, keywords=keywords, response=response)
                )

    # Helper functions to avoid late-binding
    def _apply_regex(self, text: str, pattern: str, response: str) -> str:
        return re.sub(pattern, response, text)

    def _apply_append(self, text: str, response: str) -> str:
        return text + "\n\n" + response

    def _apply_protect(self, text: str, keywords: List[str], response: str) -> str:
        lowered = text.lower()
        if any(kw in lowered for kw in keywords):
            return response
        return text

    def process(self, text: str) -> str:
        for rule in self.rules:
            text = rule(text)
        return text
