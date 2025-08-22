from pydantic import BaseModel, Field
from typing import List, Literal


class IntakeAgentOutput(BaseModel):
    title: str = Field(..., description="Title of the intake content")
    date: str = Field(..., description="Date of agreement")
    clauses: List[str] = Field(
        ..., description="Clauses associated with the intake content"
    )


class Summary(BaseModel):
    high_risk: int
    medium_risk: int
    ok: int
    total: int


class Issue(BaseModel):
    clause: str
    risk: Literal["HIGH", "MEDIUM", "OK"]
    category: str
    rationale: str
    recommendation: str
    reference: str


class AnalysisResult(BaseModel):
    summary: Summary
    issues: List[Issue]
    buckets: List[str]
