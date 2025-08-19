from server.agents.base_agent import BaseAgent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser


class AnalyserAgent(BaseAgent):
    """
    AnalyserAgent uses LangChain and Gemini to extract, classify, and risk-assess lease clauses.
    Produces output for UI: risk buckets, clause counts, and recommendations.
    """

    def __init__(self, rulebook, model_name=None, api_key=None):
        super().__init__()
        self.rulebook = rulebook

    def analyse(self, lease_text: str):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
You are a Singapore tenancy agreement analyser. Given a lease, extract all clauses, classify them into:
- Unfair Clauses (one-sided, favoring landlord)
- Stamp Duty (deadlines, responsibility)
- Your Rights (tenant protections)

For each clause, check against the rulebook below. Flag HIGH risk (illegal/excessive), MEDIUM (unfair/atypical), or OK. For each flag, provide:
- Clause text
- Risk level (HIGH/MEDIUM/OK)
- Category (Unfair Clauses / Stamp Duty / Your Rights)
- Short rationale (why flagged)
- Recommendation (how to negotiate/fix)
- Reference (industry norm or legal basis, if any)

Rulebook:
{self.rulebook}

Output JSON with:
- summary: {{ "high_risk": int, "medium_risk": int, "ok": int, "total": int }}
- issues: [{{ "clause": str, "risk": str, "category": str, "rationale": str, "recommendation": str, "reference": str }}]
- buckets: ["Unfair Clauses", "Stamp Duty", "Your Rights"]
                    """,
                ),
                ("user", lease_text),
            ]
        )

        parser = JsonOutputParser()
        chain = prompt | self.llm | parser
        return chain.invoke({})
