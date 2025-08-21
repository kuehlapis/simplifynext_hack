from pydantic import BaseModel, Field
from typing import List


class IntakeAgentOutput(BaseModel):
    title: str = Field(..., description="Title of the intake content")
    clauses: List[str] = Field(
        ..., description="Clauses associated with the intake content"
    )
