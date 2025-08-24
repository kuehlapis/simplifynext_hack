from typing import TypedDict, Dict, List, Optional, Tuple, Type, TypeVar
import re, time, collections, yaml
from pydantic import BaseModel

# ---- Your provided BaseAgent ----
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from server.util.config import getConfig

T = TypeVar("T", bound=BaseModel)

class BaseAgent:
    config = getConfig()
    API_KEY = config.get_gemini_api()

    def __init__(self):
        self.client = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.API_KEY,
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", "{system_prompt}"), ("human", "{input}")]
        )

    def get_system_prompt(self, agent_type: str) -> str:
        try:
            with open("server/agents/prompts/agent_prompts.yaml", "r") as f:
                data = yaml.safe_load(f)
                system_prompt = data["prompts"].get(agent_type, data["prompts"]["base"])
            return system_prompt
        except Exception as e:
            print(f"Error getting system prompt for {agent_type}: {e} ")

    def run(self, system_prompt: str, input: str, schema: Type[T]) -> T:
        try:
            structured_client = self.client.with_structured_output(schema)
            chain = self.prompt | structured_client
            response: T = chain.invoke({"system_prompt": system_prompt, "input": input})
            return response
        except Exception as e:
            print(f"Error running client: {e}")

# ---- Guardrail types ----
class QAState(TypedDict, total=False):
    user_id: str               # required
    draft: str                 # required (from your Planner & Drafter)
    final: str
    pii_hits: Dict[str, List[str]]
    disclaimer_added: bool
    issues: List[str]
    rate_blocked: bool

class QAGuardrailAgent(BaseAgent):
    """
    QA Guardrail Agent that *inherits from your BaseAgent* (Gemini-backed).

    Pipeline:
      1) Per-user rate limiting (sliding 1h window)
      2) PII redaction (SG-focused)
      3) Disclaimer enforcement
      4) Optional policy review via BaseAgent.run() using a Pydantic schema
      5) Final assembly
    """

    DEFAULT_DISCLAIMER = (
        "⚠️ Not legal advice. General info for **Singapore** tenant rights only. "
        "Laws/policies change; verify with official sources or a qualified lawyer."
    )

    DEFAULT_PII_PATTERNS: Dict[str, re.Pattern] = {
        "nric_fin": re.compile(r"\b[STFGM]\d{7}[A-Z]\b", re.I),          # SG NRIC/FIN
        "phone":    re.compile(r"\b(?:\+65\s?)?(?:6|8|9)\d{7}\b"),        # common SG phones
        "email":    re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", re.I),
    }

    DEFAULT_GUARDRAIL_PROMPT = (
        "You are a compliance checker for a Singapore tenant-rights info bot. "
        "Rules: (1) Do not give individualized legal advice or directives; "
        "(2) Keep scope Singapore-only; (3) If context is uncertain, say so; "
        "(4) Avoid confident claims about rights/penalties without citing a source; "
        "(5) Be neutral and informational. Return only JSON matching the schema."
    )

    class PolicyReviewModel(BaseModel):
        issues: List[str] = []  # empty == OK

    def __init__(
        self,
        *,
        disclaimer: Optional[str] = None,
        max_per_hour: int = 20,
        pii_patterns: Optional[Dict[str, re.Pattern]] = None,
        enable_policy_review: bool = True,
        agent_type: str = "qa_guardrail",
    ) -> None:
        super().__init__()
        self.disclaimer = disclaimer or self.DEFAULT_DISCLAIMER
        self.max_per_hour = max_per_hour
        self.pii_patterns = pii_patterns or self.DEFAULT_PII_PATTERNS
        self._window: Dict[str, collections.deque] = collections.defaultdict(collections.deque)
        self.enable_policy_review = enable_policy_review
        self.agent_type = agent_type

    # -------- Public API --------
    def invoke(self, state: QAState) -> QAState:
        self._validate_state(state)

        # 1) Rate limit
        msg = self._rate_check(state["user_id"])
        if msg:
            state["rate_blocked"] = True
            state["final"] = f"{self.disclaimer}\n\n{msg}"
            return state
        state["rate_blocked"] = False

        # 2) PII redaction
        draft, hits = self._redact_pii(state["draft"])
        state["draft"], state["pii_hits"] = draft, hits

        # 3) Ensure disclaimer
        with_disc, added = self._ensure_disclaimer(state["draft"])
        state["draft"], state["disclaimer_added"] = with_disc, added

        # 4) Optional policy review (Gemini via BaseAgent)
        state["issues"] = self._policy_review(state["draft"]) if self.enable_policy_review else []

        # 5) Finalize
        state["final"] = self._finalize(state)
        return state

    # -------- Internals --------
    def _validate_state(self, state: QAState) -> None:
        if "user_id" not in state or not state["user_id"]:
            raise ValueError("state['user_id'] is required")
        if "draft" not in state or not isinstance(state["draft"], str):
            raise ValueError("state['draft'] is required and must be a string")

    def _rate_check(self, user_id: str) -> Optional[str]:
        now = time.time()
        dq = self._window[user_id]
        while dq and now - dq[0] > 3600:
            dq.popleft()
        if len(dq) >= self.max_per_hour:
            return f"Rate limit reached ({self.max_per_hour}/hour). Please try later."
        dq.append(now)
        return None

    def _redact_pii(self, text: str) -> Tuple[str, Dict[str, List[str]]]:
        hits: Dict[str, List[str]] = {}
        redrafted = text
        for key, rx in self.pii_patterns.items():
            found = rx.findall(redrafted)
            if found:
                hits[key] = list(found) if isinstance(found, (list, tuple)) else [found]
                redrafted = rx.sub(f"[REDACTED_{key.upper()}]", redrafted)
        return redrafted, hits

    def _ensure_disclaimer(self, text: str) -> Tuple[str, bool]:
        if self.disclaimer.lower() in text.lower():
            return text, False
        return f"{self.disclaimer}\n\n{text}", True

    def _policy_review(self, draft_with_disclaimer: str) -> List[str]:
        try:
            system_prompt = self.get_system_prompt(self.agent_type) or self.DEFAULT_GUARDRAIL_PROMPT
        except Exception:
            system_prompt = self.DEFAULT_GUARDRAIL_PROMPT

        review_input = (
            "Review the following draft for the Singapore tenant-rights info bot. "
            "Return a JSON object with 'issues': a list of short strings, or an empty list if OK.\n\n"
            f"DRAFT:\n{draft_with_disclaimer}"
        )

        try:
            result = self.run(system_prompt=system_prompt, input=review_input, schema=self.PolicyReviewModel)
            if result and getattr(result, "issues", None) is not None:
                return list(result.issues)
        except Exception:
            pass  # fail-open to no issues
        return []

    def _finalize(self, state: QAState) -> str:
        pii_note = "\n\n(We redacted detected personal data before processing.)" if state.get("pii_hits") else ""
        issues = "\n\n⚠️ QA notes:\n- " + "\n- ".join(state["issues"]) if state.get("issues") else ""
        return f"{state['draft']}{pii_note}{issues}"
