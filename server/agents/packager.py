from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
# from server.agents.base_agent import BaseAgent
import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
try:
    from supabase import create_client
except Exception:
    create_client = None


class PackagerAgent:
    """
    Packager agent that takes outputs from analyser_agent and intake_agent
    to create a dashboard.json for the frontend and artifact links.
    """

    def __init__(self):
        self.output_dir = Path("agents/outputs")
        self.artifacts_dir = Path("agents/outputs/artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)
        self.download_dir = Path("agents/outputs/download")
        self.download_dir.mkdir(exist_ok=True)
        # Optional Supabase client
        self.supabase_url = os.getenv("SUPABASE_URL", "").strip()
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY", "").strip()
        self.supabase_bucket = os.getenv("SUPABASE_BUCKET", "artifacts").strip()
        self.supabase = None
        if self.supabase_url and self.supabase_key and create_client is not None:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                print(f"Failed to init Supabase client: {e}")

    class Artifact(BaseModel):
        id: str
        name: str
        type: str
        url: str
        description: Optional[str] = None

    def package_dashboard(
        self, intake_json: Dict[str, Any], analysis_json: Dict[str, Any]
    ) -> Dict[str, Any]:
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
                    "document_id": self._generate_document_id(title, date),
                },
                "risk_summary": {
                    "high": summary.get("high_risk", 0),
                    "medium": summary.get("medium_risk", 0),
                    "ok": summary.get("ok", 0),
                    "total": summary.get("total", 0),
                },
                "flagged_clauses": flagged_clauses,
                "artifacts": [a.model_dump() for a in artifacts],
                "categories": buckets,
            }

            # Save dashboard.json
            dashboard_path = self.output_dir / "dashboard.json"
            with open(dashboard_path, "w", encoding="utf-8") as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

            print(f"Dashboard saved to {dashboard_path}")
            return dashboard_data

        except Exception as e:
            raise RuntimeError(f"Failed to package dashboard: {e}")

    def create_frontend_package(
        self, intake_json: Dict[str, Any], analysis_json: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a comprehensive package for the frontend that includes all artifacts
        and data in a single JSON structure.
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

            # Transform issues to match frontend format
            flagged_clauses = self._transform_issues_to_clauses(issues, clauses)

            # Create comprehensive frontend package
            frontend_package = {
                "metadata": {
                    "title": title,
                    "date": date,
                    "generated_at": datetime.now().isoformat(),
                    "document_id": self._generate_document_id(title, date),
                    "version": "1.0",
                    "package_type": "frontend_ready"
                },
                "risk_summary": {
                    "high": summary.get("high_risk", 0),
                    "medium": summary.get("medium_risk", 0),
                    "ok": summary.get("ok", 0),
                    "total": summary.get("total", 0),
                },
                "flagged_clauses": flagged_clauses,
                "categories": buckets,
                "artifacts": {
                    "negotiation_rider": self._get_negotiation_rider_content(analysis_json),
                    "tenant_email": self._get_tenant_email_content(analysis_json),
                    "planner_summary": self._get_planner_summary_content(),
                    "calendar_event": self._get_calendar_event_content(intake_data),
                    "agreement_summary": self._get_agreement_summary_content(intake_data, analysis_json)
                },
                "recommendations": {
                    "top_actions": self._generate_top_recommendations(issues),
                    "priority_issues": [
                        {
                            "clause": issue.get("clause", "")[:100] + "..." if len(issue.get("clause", "")) > 100 else issue.get("clause", ""),
                            "risk": issue.get("risk", "HIGH"),
                            "category": issue.get("category", "Unknown"),
                            "recommendation": issue.get("recommendation", ""),
                            "rationale": issue.get("rationale", "")
                        }
                        for issue in issues[:10]  # Top 10 priority issues
                    ]
                },
                "document_analysis": {
                    "total_clauses": len(clauses),
                    "risk_distribution": {
                        "high_risk_percentage": round((summary.get("high_risk", 0) / max(summary.get("total", 1), 1)) * 100, 1),
                        "medium_risk_percentage": round((summary.get("medium_risk", 0) / max(summary.get("total", 1), 1)) * 100, 1),
                        "safe_percentage": round((summary.get("ok", 0) / max(summary.get("total", 1), 1)) * 100, 1)
                    },
                    "category_breakdown": self._get_category_breakdown(issues)
                }
            }

            # Save frontend package
            frontend_package_path = self.output_dir / "frontend_package.json"
            with open(frontend_package_path, "w", encoding="utf-8") as f:
                json.dump(frontend_package, f, ensure_ascii=False, indent=2)

            # Also copy to download directory
            download_frontend_path = self.download_dir / "frontend_package.json"
            with open(download_frontend_path, "w", encoding="utf-8") as f:
                json.dump(frontend_package, f, ensure_ascii=False, indent=2)

            print(f"Frontend package saved to {frontend_package_path} and {download_frontend_path}")
            return frontend_package

        except Exception as e:
            raise RuntimeError(f"Failed to create frontend package: {e}")

    def _create_artifact_links(
        self, intake_data: Dict[str, Any], analysis_json: Dict[str, Any]
    ) -> List["PackagerAgent.Artifact"]:
        """
        Create artifact links for the generated documents.
        """
        artifacts: List[PackagerAgent.Artifact] = []

        # Create calendar event artifact
        calendar_artifact = self._create_calendar_artifact(intake_data)
        if calendar_artifact:
            artifacts.append(self._maybe_upload_artifact(calendar_artifact))

        # Create email artifact
        email_artifact = self._create_email_artifact(analysis_json)
        if email_artifact:
            artifacts.append(self._maybe_upload_artifact(email_artifact))

        # Skip PDF summary to keep exactly three artifacts as requested

        # Create negotiation rider artifact
        rider_artifact = self._create_negotiation_rider_artifact(analysis_json)
        if rider_artifact:
            artifacts.append(self._maybe_upload_artifact(rider_artifact))

        # Create planner PDF artifact (from planner-agent.json)
        planner_pdf_artifact = self._create_planner_pdf_artifact()
        if planner_pdf_artifact:
            artifacts.append(self._maybe_upload_artifact(planner_pdf_artifact))

        return artifacts

    def _create_calendar_artifact(
        self, intake_data: Dict[str, Any]
    ) -> Optional["PackagerAgent.Artifact"]:
        """Create a calendar event for agreement review meeting."""
        try:
            # Prefer planner_agent generated ICS if available
            planner_ics = self.output_dir / "planner_event.ics"
            if planner_ics.exists():
                return self.Artifact(
                    id=f"calendar_{self._generate_uid()}",
                    name="Agreement Review Meeting",
                    type="ics",
                    url=str(planner_ics),
                    description="Calendar event from planner agent",
                )

            # Try to ask PlannerAgent to create it from intake
            try:
                from server.agents.planner_agent import PlannerAgent

                planner = PlannerAgent()
                created_path = planner.create_signing_ics_from_intake()
                if created_path and Path(created_path).exists():
                    return self.Artifact(
                        id=f"calendar_{self._generate_uid()}",
                        name="Agreement Review Meeting",
                        type="ics",
                        url=str(created_path),
                        description="Calendar event from planner agent",
                    )
            except Exception as inner_e:
                print(f"PlannerAgent ICS generation failed, falling back: {inner_e}")

            # Fallback: generate a simple ICS one week from now
            meeting_start = (datetime.now() + timedelta(days=7)).replace(
                hour=14, minute=0, second=0, microsecond=0
            )
            meeting_end = meeting_start + timedelta(hours=1)
            ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:PackagerAgent
BEGIN:VEVENT
UID:{self._generate_uid()}
DTSTAMP:{datetime.now().strftime("%Y%m%dT%H%M%SZ")}
DTSTART:{meeting_start.strftime("%Y%m%dT%H%M%SZ")}
DTEND:{meeting_end.strftime("%Y%m%dT%H%M%SZ")}
SUMMARY:Review Rental Agreement - {intake_data.get("title", "Agreement Review")}
DESCRIPTION:Meeting to review rental agreement clauses and discuss negotiation points
LOCATION:Virtual Meeting
END:VEVENT
END:VCALENDAR"""
            ics_filename = f"agreement_review_{datetime.now().strftime('%Y%m%d')}.ics"
            ics_path = self.artifacts_dir / ics_filename
            with open(ics_path, "w", encoding="utf-8") as f:
                f.write(ics_content)
            return self.Artifact(
                id=f"calendar_{self._generate_uid()}",
                name="Agreement Review Meeting",
                type="ics",
                url=str(ics_path),
                description="Calendar event for agreement review meeting",
            )

        except Exception as e:
            print(f"Failed to create calendar artifact: {e}")
            return None

    def _create_email_artifact(
        self, analysis_json: Dict[str, Any]
    ) -> Optional["PackagerAgent.Artifact"]:
        """Create an email template for the tenant."""
        try:
            high_risk_issues = [
                issue
                for issue in analysis_json.get("issues", [])
                if issue.get("risk") == "HIGH"
            ]

            email_content = {
                "subject": "High-Risk Clauses in Your Rental Agreement - Action Required",
                "body": self._generate_email_body(high_risk_issues),
                "recommendations": [
                    issue.get("recommendation", "") for issue in high_risk_issues[:5]
                ],
            }

            # Save email JSON
            email_filename = f"tenant_email_{datetime.now().strftime('%Y%m%d')}.json"
            email_path = self.artifacts_dir / email_filename

            with open(email_path, "w", encoding="utf-8") as f:
                json.dump(email_content, f, ensure_ascii=False, indent=2)

            return self.Artifact(
                id=f"email_{self._generate_uid()}",
                name="Tenant Notification Email",
                type="email",
                url=str(email_path),
                description="Email template for tenant notification",
            )

        except Exception as e:
            print(f"Failed to create email artifact: {e}")
            return None

    def _create_summary_pdf_artifact(
        self, intake_data: Dict[str, Any], analysis_json: Dict[str, Any]
    ) -> Optional["PackagerAgent.Artifact"]:
        """Create a summary PDF built from analyser_agent output and intake metadata."""
        try:
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Paragraph,
                    Spacer,
                    Table,
                    TableStyle,
                )
                from reportlab.lib import colors
                from reportlab.pdfgen import canvas
            except Exception as import_error:
                raise RuntimeError(
                    f"PDF generation requires reportlab. Install it to enable PDFs: {import_error}"
                )

            title = intake_data.get("title", "Rental Agreement Summary")
            date_str_meta = intake_data.get("date", "")
            risk_summary = analysis_json.get("summary", {})
            issues = analysis_json.get("issues", [])

            date_str = datetime.now().strftime('%Y%m%d')
            summary_filename = f"agreement_summary_{date_str}.pdf"
            summary_path = self.artifacts_dir / summary_filename

            def build_story() -> list:
                styles = getSampleStyleSheet()
                story_local = []
                story_local.append(Paragraph(title, styles["Title"]))
                if date_str_meta:
                    story_local.append(Paragraph(f"Agreement Date: {date_str_meta}", styles["Normal"]))
                story_local.append(Paragraph(f"Generated at: {datetime.now().isoformat()}", styles["Normal"]))
                story_local.append(Spacer(1, 12))

                table_data = [
                    ["High", "Medium", "OK", "Total"],
                    [
                        str(risk_summary.get("high_risk", 0)),
                        str(risk_summary.get("medium_risk", 0)),
                        str(risk_summary.get("ok", 0)),
                        str(risk_summary.get("total", 0)),
                    ],
                ]
                table = Table(table_data)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                        ]
                    )
                )
                story_local.append(table)
                story_local.append(Spacer(1, 18))

                styles_h2 = styles["Heading2"]
                story_local.append(Paragraph("Top Issues", styles_h2))
                story_local.append(Spacer(1, 6))
                for idx, issue in enumerate(issues[:10], start=1):
                    category = issue.get("category", "Issue")
                    risk = issue.get("risk", "-")
                    clause_snippet = issue.get("clause", "")
                    rationale = issue.get("rationale", "")
                    recommendation = issue.get("recommendation", "")
                    reference = issue.get("reference", "")

                    if rationale and clause_snippet and rationale.strip() == clause_snippet.strip():
                        rationale = reference or ""
                    if rationale and clause_snippet and clause_snippet.strip() in rationale.strip() and len(rationale.strip()) <= len(clause_snippet.strip()) + 10:
                        rationale = reference or ""

                    story_local.append(Paragraph(f"{idx}. <b>{category}</b> - Risk: <b>{risk}</b>", styles["Normal"]))
                    if clause_snippet:
                        story_local.append(Paragraph(f"Clause: {clause_snippet}", styles["Normal"]))
                    if rationale:
                        story_local.append(Paragraph(f"Rationale: {rationale}", styles["Normal"]))
                    if recommendation:
                        story_local.append(Paragraph(f"Recommendation: {recommendation}", styles["Normal"]))
                    story_local.append(Spacer(1, 10))

                return story_local

            doc = SimpleDocTemplate(str(summary_path), pagesize=A4)
            story = build_story()

            try:
                doc.build(story)
            except PermissionError:
                summary_filename = f"agreement_summary_{date_str}_{self._generate_uid()}.pdf"
                summary_path = self.artifacts_dir / summary_filename
                doc = SimpleDocTemplate(str(summary_path), pagesize=A4)
                doc.build(story)

            # Ensure file has at least one page; if not, write minimal fallback
            try:
                if not summary_path.exists() or summary_path.stat().st_size <= 0:
                    raise IOError("PDF appears empty; regenerating with canvas fallback")
            except Exception:
                fallback_filename = f"agreement_summary_{date_str}_{self._generate_uid()}.pdf"
                summary_path = self.artifacts_dir / fallback_filename
                c = canvas.Canvas(str(summary_path), pagesize=A4)
                c.setFont("Helvetica-Bold", 16)
                c.drawString(72, 800, title)
                c.setFont("Helvetica", 10)
                c.drawString(72, 785, f"Generated at: {datetime.now().isoformat()}")
                c.setFont("Helvetica", 12)
                c.drawString(72, 760, "Risk Summary:")
                c.drawString(90, 740, f"High: {risk_summary.get('high_risk', 0)}  Medium: {risk_summary.get('medium_risk', 0)}  OK: {risk_summary.get('ok', 0)}  Total: {risk_summary.get('total', 0)}")
                if issues:
                    first = issues[0]
                    c.drawString(72, 710, f"1. {first.get('category', 'Issue')} - Risk: {first.get('risk', '-')}")
                    c.setFont("Helvetica", 10)
                    clause = first.get('clause', '')
                    rationale = first.get('rationale', '')
                    recommendation = first.get('recommendation', '')
                    c.drawString(90, 695, f"Clause: {clause[:100]}")
                    c.drawString(90, 680, f"Rationale: {rationale[:100]}")
                    c.drawString(90, 665, f"Recommendation: {recommendation[:100]}")
                c.showPage()
                c.save()

            return self.Artifact(
                id=f"pdf_{self._generate_uid()}",
                name="Agreement Summary Report",
                type="pdf",
                url=str(summary_path),
                description="Comprehensive summary of agreement analysis",
            )

        except Exception as e:
            print(f"Failed to create summary PDF artifact: {e}")
            return None

    def _create_negotiation_rider_artifact(
        self, analysis_json: Dict[str, Any]
    ) -> Optional["PackagerAgent.Artifact"]:
        """Create a negotiation rider document."""
        try:
            high_risk_issues = [
                issue
                for issue in analysis_json.get("issues", [])
                if issue.get("risk") == "HIGH"
            ]

            rider_content = {
                "title": "Negotiation Rider - Proposed Changes",
                "purpose": "This document outlines proposed changes to address unfair clauses in the rental agreement",
                "proposed_changes": [
                    {
                        "original_clause": issue.get("clause", ""),
                        "proposed_change": issue.get("recommendation", ""),
                        "rationale": issue.get("rationale", ""),
                        "category": issue.get("category", ""),
                    }
                    for issue in high_risk_issues[:15]  # Top 15 issues
                ],
                "legal_basis": "Based on Singapore rental law and industry standards",
                "generated_at": datetime.now().isoformat(),
            }

            # Save rider JSON
            rider_filename = (
                f"negotiation_rider_{datetime.now().strftime('%Y%m%d')}.json"
            )
            rider_path = self.artifacts_dir / rider_filename

            with open(rider_path, "w", encoding="utf-8") as f:
                json.dump(rider_content, f, ensure_ascii=False, indent=2)

            return self.Artifact(
                id=f"rider_{self._generate_uid()}",
                name="Negotiation Rider",
                type="rider",
                url=str(rider_path),
                description="Document outlining proposed changes to unfair clauses",
            )

        except Exception as e:
            print(f"Failed to create negotiation rider artifact: {e}")
            return None

    def _create_planner_pdf_artifact(self) -> Optional["PackagerAgent.Artifact"]:
        """Create a PDF from planner-agent.json (subject, body, recommendations)."""
        try:
            # Attempt to import reportlab; if not installed, skip gracefully
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Paragraph,
                    Spacer,
                    ListFlowable,
                    ListItem,
                )
                from reportlab.lib import colors
            except Exception as import_error:
                print(
                    f"Planner PDF generation requires reportlab. Skipping planner PDF: {import_error}"
                )
                return None

            # Read planner output
            try:
                from server.agents.planner_agent import PlannerAgent
            except Exception:
                # Fallback local import if running as script
                from .planner_agent import PlannerAgent  # type: ignore

            planner = PlannerAgent()
            planner_path = Path(planner.output_file)
            if not planner_path.exists():
                return None

            with open(planner_path, "r", encoding="utf-8") as f:
                planner_json = json.load(f)

            subject = planner_json.get("subject") or planner_json.get("title") or "Planner Output"
            body = planner_json.get("body") or planner_json.get("content") or ""
            recs = planner_json.get("recommendations") or planner_json.get("tasks") or []
            if not isinstance(recs, list):
                recs = [str(recs)]

            pdf_filename = f"planner_summary_{datetime.now().strftime('%Y%m%d')}.pdf"
            pdf_path = self.artifacts_dir / pdf_filename

            styles = getSampleStyleSheet()
            story: list = []
            story.append(Paragraph(subject, styles["Title"]))
            story.append(Paragraph(f"Generated at: {datetime.now().isoformat()}", styles["Normal"]))
            story.append(Spacer(1, 16))
            if body:
                story.append(Paragraph("Summary Email Draft", styles["Heading2"]))
                story.append(Spacer(1, 6))
                # Split body to avoid overly long paragraphs
                for para in str(body).split("\n\n"):
                    story.append(Paragraph(para.strip().replace("\n", "<br/>"), styles["Normal"]))
                    story.append(Spacer(1, 6))

            if recs:
                story.append(Spacer(1, 10))
                story.append(Paragraph("Top Recommendations", styles["Heading2"]))
                story.append(Spacer(1, 6))
                bullet_items = [
                    ListItem(Paragraph(str(r), styles["Normal"])) for r in recs[:15]
                ]
                story.append(
                    ListFlowable(
                        bullet_items,
                        bulletType="bullet",
                        start="circle",
                        bulletColor=colors.darkblue,
                        leftIndent=18,
                    )
                )

            doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
            try:
                doc.build(story)
            except PermissionError:
                pdf_filename = f"planner_summary_{datetime.now().strftime('%Y%m%d')}_{self._generate_uid()}.pdf"
                pdf_path = self.artifacts_dir / pdf_filename
                doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
                doc.build(story)

            return self.Artifact(
                id=f"pdf_{self._generate_uid()}",
                name="Planner Summary",
                type="pdf",
                url=str(pdf_path),
                description="PDF generated from planner-agent output",
            )

        except Exception as e:
            print(f"Failed to create planner PDF artifact: {e}")
            return None

    def _maybe_upload_artifact(self, artifact: "PackagerAgent.Artifact") -> "PackagerAgent.Artifact":
        """Upload artifact file to Supabase Storage if configured and return updated artifact with public URL."""
        try:
            if not self.supabase:
                return artifact
            local_url = artifact.url
            if not local_url:
                return artifact
            local_path = Path(local_url)
            if not local_path.exists():
                return artifact
            date_prefix = datetime.now().strftime('%Y/%m/%d')
            destination = f"{date_prefix}/{local_path.name}"
            content_type_map = {
                ".pdf": "application/pdf",
                ".json": "application/json",
                ".ics": "text/calendar",
            }
            content_type = content_type_map.get(local_path.suffix.lower(), "application/octet-stream")
            with open(local_path, "rb") as f:
                self.supabase.storage.from_(self.supabase_bucket).upload(
                    file=f,
                    path=destination,
                    file_options={"contentType": content_type, "upsert": True},
                )
            public_url = self.supabase.storage.from_(self.supabase_bucket).get_public_url(destination)
            artifact.url = public_url
            return artifact
        except Exception as e:
            print(f"Supabase upload failed: {e}")
            return artifact

    def _transform_issues_to_clauses(
        self, issues: List[Dict[str, Any]], original_clauses: List[str]
    ) -> List[Dict[str, Any]]:
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
                "anchor": f"clause_{original_index}" if original_index >= 0 else None,
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
        return hashlib.md5(
            f"{datetime.now().isoformat()}_{os.getpid()}".encode()
        ).hexdigest()[:8]

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

            # Create frontend package
            frontend_package = self.create_frontend_package(intake_json, analysis_json)

            print("Packaging completed successfully!")
            print("Created both dashboard.json and frontend_package.json")
            return {
                "dashboard": dashboard_data,
                "frontend_package": frontend_package
            }

        except Exception as e:
            raise RuntimeError(f"Packaging failed: {e}")

    def _get_negotiation_rider_content(self, analysis_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract negotiation rider content for frontend."""
        try:
            high_risk_issues = [
                issue
                for issue in analysis_json.get("issues", [])
                if issue.get("risk") == "HIGH"
            ]

            return {
                "title": "Negotiation Rider - Proposed Changes",
                "purpose": "This document outlines proposed changes to address unfair clauses in the rental agreement",
                "proposed_changes": [
                    {
                        "original_clause": issue.get("clause", ""),
                        "proposed_change": issue.get("recommendation", ""),
                        "rationale": issue.get("rationale", ""),
                        "category": issue.get("category", ""),
                    }
                    for issue in high_risk_issues[:15]  # Top 15 issues
                ],
                "legal_basis": "Based on Singapore rental law and industry standards",
                "generated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Failed to get negotiation rider content: {e}")
            return {"error": "Failed to generate negotiation rider content"}

    def _get_tenant_email_content(self, analysis_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tenant email content for frontend."""
        try:
            high_risk_issues = [
                issue
                for issue in analysis_json.get("issues", [])
                if issue.get("risk") == "HIGH"
            ]

            return {
                "subject": "High-Risk Clauses in Your Rental Agreement - Action Required",
                "body": self._generate_email_body(high_risk_issues),
                "recommendations": [
                    issue.get("recommendation", "") for issue in high_risk_issues[:5]
                ],
                "generated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Failed to get tenant email content: {e}")
            return {"error": "Failed to generate tenant email content"}

    def _get_planner_summary_content(self) -> Dict[str, Any]:
        """Extract planner summary content for frontend."""
        try:
            planner_path = self.output_dir / "planner-agent.json"
            if planner_path.exists():
                with open(planner_path, "r", encoding="utf-8") as f:
                    planner_json = json.load(f)
                
                return {
                    "subject": planner_json.get("subject", "Planner Summary"),
                    "body": planner_json.get("body", ""),
                    "recommendations": planner_json.get("recommendations", []),
                    "generated_at": datetime.now().isoformat(),
                }
            else:
                return {
                    "subject": "Planner Summary Not Available",
                    "body": "Planner agent output not found",
                    "recommendations": [],
                    "generated_at": datetime.now().isoformat(),
                }
        except Exception as e:
            print(f"Failed to get planner summary content: {e}")
            return {"error": "Failed to get planner summary content"}

    def _get_calendar_event_content(self, intake_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract calendar event content for frontend."""
        try:
            planner_ics = self.output_dir / "planner_event.ics"
            if planner_ics.exists():
                with open(planner_ics, "r", encoding="utf-8") as f:
                    ics_content = f.read()
                
                return {
                    "title": "Agreement Review Meeting",
                    "description": "Meeting to review rental agreement clauses and discuss negotiation points",
                    "ics_content": ics_content,
                    "generated_at": datetime.now().isoformat(),
                }
            else:
                # Generate a simple calendar event
                meeting_start = (datetime.now() + timedelta(days=7)).replace(
                    hour=14, minute=0, second=0, microsecond=0
                )
                meeting_end = meeting_start + timedelta(hours=1)
                
                return {
                    "title": "Agreement Review Meeting",
                    "description": "Meeting to review rental agreement clauses and discuss negotiation points",
                    "scheduled_date": meeting_start.isoformat(),
                    "duration_hours": 1,
                    "generated_at": datetime.now().isoformat(),
                }
        except Exception as e:
            print(f"Failed to get calendar event content: {e}")
            return {"error": "Failed to get calendar event content"}

    def _get_agreement_summary_content(self, intake_data: Dict[str, Any], analysis_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract agreement summary content for frontend."""
        try:
            summary = analysis_json.get("summary", {})
            issues = analysis_json.get("issues", [])
            
            return {
                "title": intake_data.get("title", "Rental Agreement Summary"),
                "agreement_date": intake_data.get("date", ""),
                "risk_overview": {
                    "high_risk_count": summary.get("high_risk", 0),
                    "medium_risk_count": summary.get("medium_risk", 0),
                    "safe_count": summary.get("ok", 0),
                    "total_clauses": summary.get("total", 0)
                },
                "key_issues": [
                    {
                        "clause": issue.get("clause", "")[:150] + "..." if len(issue.get("clause", "")) > 150 else issue.get("clause", ""),
                        "risk": issue.get("risk", "HIGH"),
                        "category": issue.get("category", "Unknown"),
                        "recommendation": issue.get("recommendation", "")
                    }
                    for issue in issues[:20]  # Top 20 issues
                ],
                "generated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Failed to get agreement summary content: {e}")
            return {"error": "Failed to get agreement summary content"}

    def _get_category_breakdown(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get breakdown of issues by category."""
        try:
            category_counts = {}
            for issue in issues:
                category = issue.get("category", "Unknown")
                if category not in category_counts:
                    category_counts[category] = {"total": 0, "high": 0, "medium": 0, "ok": 0}
                
                category_counts[category]["total"] += 1
                risk = issue.get("risk", "OK")
                if risk in category_counts[category]:
                    category_counts[category][risk.lower()] += 1
            
            return category_counts
        except Exception as e:
            print(f"Failed to get category breakdown: {e}")
            return {}


if __name__ == "__main__":
    # Test the packager agent
    packager = PackagerAgent()
    try:
        result = packager.run_packaging()
        print("\n=== Dashboard Data ===")
        print(json.dumps(result["dashboard"], indent=2))
        print("\n=== Frontend Package ===")
        print(json.dumps(result["frontend_package"], indent=2))
    except Exception as e:
        print(f"Error: {e}")
