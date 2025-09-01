from __future__ import annotations
from typing import List, Dict, Any, Literal
from server.agents.base_agent import BaseAgent
from pydantic import BaseModel, Field
import json
from pathlib import Path


class RiskCounts(BaseModel):
    high: int = Field(0, description="Count of high risk issues")
    medium: int = Field(0, description="Count of medium risk issues")
    ok: int = Field(0, description="Count of clauses that are ok")


class FlaggedClause(BaseModel):
    id: str = Field(..., description="Unique identifier for the clause")
    category: Literal[
        "Unfair Clauses", "Your Rights", "Stamp Duty", "Legal Issues", "Financial Terms"
    ] = Field(..., description="Category of the issue")
    risk: Literal["HIGH", "MEDIUM", "OK"] = Field(
        ..., description="Risk level of the issue"
    )
    title: str = Field(..., description="Short title describing the issue")
    description: str = Field(..., description="Detailed description of the issue")
    anchor: str = Field(..., description="Reference to the clause location")


class Artifact(BaseModel):
    id: str = Field(..., description="Unique identifier for the artifact")
    name: str = Field(..., description="Display name of the artifact")
    type: Literal["ics", "email", "rider", "pdf"] = Field(
        ..., description="Type of artifact"
    )
    url: str = Field(..., description="URL to download the artifact")


class DashboardData(BaseModel):
    riskCounts: RiskCounts = Field(..., description="Summary of risk counts")
    flaggedClauses: List[FlaggedClause] = Field(
        [], description="List of flagged clauses with issues"
    )
    artifacts: List[Artifact] = Field(
        [], description="List of generated artifacts for download"
    )


class PackagerV2Agent(BaseAgent):
    """
    Packages analysis results into a format expected by the frontend dashboard.
    """

    def __init__(self):
        super().__init__()
        self.output_dir = Path("server/agents/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_file = self.output_dir / "dashboard_data.json"

    def package_results(self, analysis_result: Dict[str, Any]) -> DashboardData:
        """
        Transform analysis results into the format expected by the frontend.
        """
        # Extract risk counts from the summary
        summary = analysis_result.get("summary", {})
        risk_counts = RiskCounts(
            high=summary.get("high_risk", 0),
            medium=summary.get("medium_risk", 0),
            ok=summary.get("ok", 0),
        )

        # Transform issues into flagged clauses
        issues = analysis_result.get("issues", [])
        flagged_clauses = []

        for i, issue in enumerate(issues):
            if issue.get("risk") in [
                "HIGH",
                "MEDIUM",
            ]:  # Only include HIGH and MEDIUM risks
                clause_id = str(i + 1)
                anchor = f"clause-{clause_id}"

                flagged_clauses.append(
                    FlaggedClause(
                        id=clause_id,
                        category=self._map_category(issue.get("category", "")),
                        risk=issue.get("risk", "MEDIUM"),
                        title=issue.get("clause", "")[
                            :50
                        ],  # Use first 50 chars as title
                        description=issue.get("rationale", ""),
                        anchor=anchor,
                    )
                )

        # Create placeholder artifacts (in a real implementation, these would come from the planner)
        artifacts = [
            Artifact(
                id="1", name="Task Schedule", type="ics", url="/download/task-schedule"
            ),
            Artifact(
                id="2",
                name="Summary Email Draft",
                type="email",
                url="/download/email-draft",
            ),
            Artifact(
                id="3",
                name="Amendment Rider",
                type="rider",
                url="/download/amendment-rider",
            ),
            Artifact(
                id="4",
                name="Annotated Agreement",
                type="pdf",
                url="/download/annotated-agreement",
            ),
        ]

        # Create the complete dashboard data
        dashboard_data = DashboardData(
            riskCounts=risk_counts, flaggedClauses=flagged_clauses, artifacts=artifacts
        )

        # Save to file for persistence
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(dashboard_data.model_dump(), f, ensure_ascii=False, indent=2)

        return dashboard_data

    def _map_category(self, category: str) -> str:
        """Map analysis categories to frontend categories."""
        category_map = {
            "unfair": "Unfair Clauses",
            "rights": "Your Rights",
            "stamp duty": "Stamp Duty",
            "legal": "Legal Issues",
            "financial": "Financial Terms",
        }

        for key, value in category_map.items():
            if key.lower() in category.lower():
                return value

        # Default category if no match
        return "Legal Issues"
