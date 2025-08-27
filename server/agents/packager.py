from __future__ import annotations
from typing import List, Dict, Any, Optional
from server.agents.base_agent import BaseAgent
from server.agents.schema import AnalysisResult, IntakeAgentOutput
import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path


class PackagerAgent(BaseAgent):
    """
    Packager agent that takes outputs from analyser_agent and intake_agent
    to create a dashboard.json for the frontend and artifact links.
    """

    def __init__(self):
        super().__init__()
        self.output_dir = Path("server/agents/outputs")
        self.artifacts_dir = Path("server/agents/outputs/artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)

    def package_dashboard(self, intake_json: Dict[str, Any], analysis_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Package the outputs into a dashboard.json format for the frontend.
        """
        try:
            # Extract data from intake agent output
            intake_data = intake_json.get("summary", {}).get("content", {})
            title = intake_data.get("title", "Unknown Agreement")
            date = intake_data.get("date", "")
            clauses = intake_data.get("clauses", [])
            
            # Extract data from analysis agent output
            summary = analysis_json.get("summary", {})
            issues = analysis_json.get("issues", [])
            buckets = analysis_json.get("buckets", [])
            
            # Create artifact links
            artifacts = self._create_artifact_links(intake_data, analysis_json)
            
            # Transform issues to match frontend format
            flagged_clauses = self._transform_issues_to_clauses(issues, clauses)
            
            # Create dashboard data structure
            dashboard_data = {
                "metadata": {
                    "title": title,
                    "date": date,
                    "generated_at": datetime.now().isoformat(),
                    "document_id": self._generate_document_id(title, date)
                },
                "risk_summary": {
                    "high": summary.get("high_risk", 0),
                    "medium": summary.get("medium_risk", 0),
                    "ok": summary.get("ok", 0),
                    "total": summary.get("total", 0)
                },
                "flagged_clauses": flagged_clauses,
                "artifacts": artifacts,
                "categories": buckets
            }
            
            # Save dashboard.json
            dashboard_path = self.output_dir / "dashboard.json"
            with open(dashboard_path, "w", encoding="utf-8") as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
            
            print(f"Dashboard saved to {dashboard_path}")
            return dashboard_data
            
        except Exception as e:
            raise RuntimeError(f"Failed to package dashboard: {e}")

    def _create_artifact_links(self, intake_data: Dict[str, Any], analysis_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create artifact links for the generated documents.
        """
        artifacts = []
        
        # Create calendar event artifact
        calendar_artifact = self._create_calendar_artifact(intake_data)
        if calendar_artifact:
            artifacts.append(calendar_artifact)
        
        # Create email artifact
        email_artifact = self._create_email_artifact(analysis_json)
        if email_artifact:
            artifacts.append(email_artifact)
        
        # Create summary PDF artifact
        pdf_artifact = self._create_summary_pdf_artifact(intake_data, analysis_json)
        if pdf_artifact:
            artifacts.append(pdf_artifact)
        
        # Create negotiation rider artifact
        rider_artifact = self._create_negotiation_rider_artifact(analysis_json)
        if rider_artifact:
            artifacts.append(rider_artifact)
        
        return artifacts

    def _create_calendar_artifact(self, intake_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a calendar event for agreement review meeting."""
        try:
            # Create a calendar event for 1 week from now (safe across month/year boundaries)
            meeting_start = (datetime.now() + timedelta(days=7)).replace(
                hour=14, minute=0, second=0, microsecond=0
            )
            meeting_end = meeting_start + timedelta(hours=1)
            
            ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:PackagerAgent
BEGIN:VEVENT
UID:{self._generate_uid()}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{meeting_start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{meeting_end.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:Review Rental Agreement - {intake_data.get('title', 'Agreement Review')}
DESCRIPTION:Meeting to review rental agreement clauses and discuss negotiation points
LOCATION:Virtual Meeting
END:VEVENT
END:VCALENDAR"""
            
            # Save ICS file
            ics_filename = f"agreement_review_{datetime.now().strftime('%Y%m%d')}.ics"
            ics_path = self.artifacts_dir / ics_filename
            
            with open(ics_path, "w", encoding="utf-8") as f:
                f.write(ics_content)
            
            return {
                "id": f"calendar_{self._generate_uid()}",
                "name": "Agreement Review Meeting",
                "type": "ics",
                "url": str(ics_path),
                "description": "Calendar event for agreement review meeting"
            }
            
        except Exception as e:
            print(f"Failed to create calendar artifact: {e}")
            return None

    def _create_email_artifact(self, analysis_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an email template for the tenant."""
        try:
            high_risk_issues = [issue for issue in analysis_json.get("issues", []) if issue.get("risk") == "HIGH"]
            
            email_content = {
                "subject": "High-Risk Clauses in Your Rental Agreement - Action Required",
                "body": self._generate_email_body(high_risk_issues),
                "recommendations": [issue.get("recommendation", "") for issue in high_risk_issues[:5]]
            }
            
            # Save email JSON
            email_filename = f"tenant_email_{datetime.now().strftime('%Y%m%d')}.json"
            email_path = self.artifacts_dir / email_filename
            
            with open(email_path, "w", encoding="utf-8") as f:
                json.dump(email_content, f, ensure_ascii=False, indent=2)
            
            return {
                "id": f"email_{self._generate_uid()}",
                "name": "Tenant Notification Email",
                "type": "email",
                "url": str(email_path),
                "description": "Email template for tenant notification"
            }
            
        except Exception as e:
            print(f"Failed to create email artifact: {e}")
            return None

    def _create_summary_pdf_artifact(self, intake_data: Dict[str, Any], analysis_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a summary document for the tenant."""
        try:
            summary_content = {
                "title": intake_data.get("title", "Rental Agreement Summary"),
                "date": intake_data.get("date", ""),
                "risk_summary": analysis_json.get("summary", {}),
                "key_issues": analysis_json.get("issues", [])[:10],  # Top 10 issues
                "recommendations": self._generate_top_recommendations(analysis_json.get("issues", [])),
                "generated_at": datetime.now().isoformat()
            }
            
            # Save summary JSON (simulating PDF structure)
            summary_filename = f"agreement_summary_{datetime.now().strftime('%Y%m%d')}.json"
            summary_path = self.artifacts_dir / summary_filename
            
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary_content, f, ensure_ascii=False, indent=2)
            
            return {
                "id": f"pdf_{self._generate_uid()}",
                "name": "Agreement Summary Report",
                "type": "pdf",
                "url": str(summary_path),
                "description": "Comprehensive summary of agreement analysis"
            }
            
        except Exception as e:
            print(f"Failed to create summary PDF artifact: {e}")
            return None

    def _create_negotiation_rider_artifact(self, analysis_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a negotiation rider document."""
        try:
            high_risk_issues = [issue for issue in analysis_json.get("issues", []) if issue.get("risk") == "HIGH"]
            
            rider_content = {
                "title": "Negotiation Rider - Proposed Changes",
                "purpose": "This document outlines proposed changes to address unfair clauses in the rental agreement",
                "proposed_changes": [
                    {
                        "original_clause": issue.get("clause", ""),
                        "proposed_change": issue.get("recommendation", ""),
                        "rationale": issue.get("rationale", ""),
                        "category": issue.get("category", "")
                    }
                    for issue in high_risk_issues[:15]  # Top 15 issues
                ],
                "legal_basis": "Based on Singapore rental law and industry standards",
                "generated_at": datetime.now().isoformat()
            }
            
            # Save rider JSON
            rider_filename = f"negotiation_rider_{datetime.now().strftime('%Y%m%d')}.json"
            rider_path = self.artifacts_dir / rider_filename
            
            with open(rider_path, "w", encoding="utf-8") as f:
                json.dump(rider_content, f, ensure_ascii=False, indent=2)
            
            return {
                "id": f"rider_{self._generate_uid()}",
                "name": "Negotiation Rider",
                "type": "rider",
                "url": str(rider_path),
                "description": "Document outlining proposed changes to unfair clauses"
            }
            
        except Exception as e:
            print(f"Failed to create negotiation rider artifact: {e}")
            return None

    def _transform_issues_to_clauses(self, issues: List[Dict[str, Any]], original_clauses: List[str]) -> List[Dict[str, Any]]:
        """Transform analysis issues to frontend clause format."""
        transformed_clauses = []
        
        for i, issue in enumerate(issues):
            # Find the original clause text
            clause_text = issue.get("clause", "")
            original_index = -1
            
            # Try to find the clause in original clauses
            for j, orig_clause in enumerate(original_clauses):
                if clause_text in orig_clause or orig_clause in clause_text:
                    original_index = j
                    break
            
            transformed_clause = {
                "id": f"clause_{i}_{self._generate_uid()}",
                "category": issue.get("category", "Unknown"),
                "risk": issue.get("risk", "OK"),
                "title": f"Clause {i + 1}: {issue.get('category', 'Issue')}",
                "description": f"{clause_text}\n\nRationale: {issue.get('rationale', '')}\n\nRecommendation: {issue.get('recommendation', '')}",
                "anchor": f"clause_{original_index}" if original_index >= 0 else None
            }
            
            transformed_clauses.append(transformed_clause)
        
        return transformed_clauses

    def _generate_email_body(self, high_risk_issues: List[Dict[str, Any]]) -> str:
        """Generate email body content."""
        body = "Dear Tenant,\n\n"
        body += "I am writing to inform you about several high-risk clauses identified in your rental agreement that require immediate attention.\n\n"
        
        for i, issue in enumerate(high_risk_issues[:5], 1):
            body += f"{i}. Clause: {issue.get('clause', '')[:100]}...\n"
            body += f"   Risk Level: {issue.get('risk', 'HIGH')}\n"
            body += f"   Recommendation: {issue.get('recommendation', '')}\n\n"
        
        body += "It is strongly recommended that you:\n"
        body += "1. Review these clauses carefully\n"
        body += "2. Consider negotiating with your landlord\n"
        body += "3. Seek legal advice if necessary\n\n"
        body += "Best regards,\nRental Agreement Analysis System"
        
        return body

    def _generate_top_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate top recommendations from issues."""
        recommendations = []
        for issue in issues[:10]:  # Top 10 recommendations
            rec = issue.get("recommendation", "")
            if rec and rec not in recommendations:
                recommendations.append(rec)
        return recommendations

    def _generate_document_id(self, title: str, date: str) -> str:
        """Generate a unique document ID."""
        content = f"{title}_{date}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _generate_uid(self) -> str:
        """Generate a unique identifier."""
        return hashlib.md5(f"{datetime.now().isoformat()}_{os.getpid()}".encode()).hexdigest()[:8]

    def run_packaging(self) -> Dict[str, Any]:
        """
        Main method to run the packaging process.
        Reads existing outputs and creates the dashboard.
        """
        try:
            # Read intake agent output
            intake_path = self.output_dir / "intake_agent.json"
            if not intake_path.exists():
                raise FileNotFoundError("intake_agent.json not found")
            
            with open(intake_path, "r", encoding="utf-8") as f:
                intake_json = json.load(f)
            
            # Read analysis agent output
            analysis_path = self.output_dir / "analysis_result.json"
            if not analysis_path.exists():
                raise FileNotFoundError("analysis_result.json not found")
            
            with open(analysis_path, "r", encoding="utf-8") as f:
                analysis_json = json.load(f)
            
            # Package the dashboard
            dashboard_data = self.package_dashboard(intake_json, analysis_json)
            
            print("Packaging completed successfully!")
            return dashboard_data
            
        except Exception as e:
            raise RuntimeError(f"Packaging failed: {e}")


if __name__ == "__main__":
    # Test the packager agent
    packager = PackagerAgent()
    try:
        result = packager.run_packaging()
        print("Dashboard data:", json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
