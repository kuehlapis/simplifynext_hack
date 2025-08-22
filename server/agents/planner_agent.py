import json


class PlannerAgent:
    # def create_signing_ics_from_intake(self, intake_file=None):
    #     """
    #     Reads intake_agent.json and creates an ICS file for signing date (1 week after agreement date).
    #     """
    #     import os
    #     from datetime import datetime, timedelta
    #     if intake_file is None:
    #         intake_file = os.path.join(os.path.dirname(__file__), "outputs", "intake_agent.json")
    #     ics_file = os.path.join(os.path.dirname(__file__), "outputs", "planner_event.ics")
    #     try:
    #         with open(intake_file, "r", encoding="utf-8") as f:
    #             intake_data = json.load(f)
    #         date_agreed = intake_data["anchor"]["content"]["document"]["agreement"]["date_agreed"]
    #         date_obj = datetime.strptime(date_agreed, "%d/%m/%y")
    #         signing_date = date_obj + timedelta(weeks=1)
    #         event_start = signing_date.strftime("%Y-%m-%d") + " 14:00:00"
    #         event_end = signing_date.strftime("%Y-%m-%d") + " 15:00:00"
    #         event_title = "Agreement Signing Meeting"
    #         # Write ICS file
    #         ics_content = (
    #             "BEGIN:VCALENDAR\n"
    #             "VERSION:2.0\n"
    #             "PRODID:planner_agent\n"
    #             "BEGIN:VEVENT\n"
    #             f"DTSTART:{signing_date.strftime('%Y%m%dT140000Z')}\n"
    #             f"DTEND:{signing_date.strftime('%Y%m%dT150000Z')}\n"
    #             f"SUMMARY:{event_title}\n"
    #             "END:VEVENT\n"
    #             "END:VCALENDAR\n"
    #         )
    #         with open(ics_file, "w", encoding="utf-8") as f:
    #             f.write(ics_content)
    #         print(f"ICS file created: {ics_file}")
    #         return ics_file
    #     except Exception as e:
    #         print(f"Error creating ICS file: {e}")
    #         return None
    def __init__(self):
        import os

        outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        self.output_file = os.path.join(outputs_dir, "planner-agent.json")

    def generate_summary_email_from_analysis(self, analysis_file=None):
        """
        Reads analysis_result.json and generates a summary email with risks and recommendations.
        """
        import os

        if analysis_file is None:
            analysis_file = os.path.join(
                os.path.dirname(__file__), "outputs", "analysis_result.json"
            )
        try:
            with open(analysis_file, "r", encoding="utf-8") as f:
                analysis = json.load(f)
        except Exception as e:
            print(f"Error reading analysis file: {e}")
            return None

        summary = analysis.get("summary", {})
        issues = analysis.get("issues", [])

        email_lines = [
            "Subject: Rental Agreement Risk Summary",
            "",
            f"High Risk Clauses: {summary.get('high_risk', 0)}",
            f"Medium Risk Clauses: {summary.get('medium_risk', 0)}",
            f"OK Clauses: {summary.get('ok', 0)}",
            f"Total Clauses Analyzed: {summary.get('total', 0)}",
            "",
            "Top Issues and Recommendations:",
        ]
        for idx, issue in enumerate(issues[:5]):  # Include top 5 issues
            email_lines.append(f"{idx + 1}. Clause: {issue['clause']}")
            email_lines.append(f"   Risk: {issue['risk']}")
            email_lines.append(f"   Rationale: {issue['rationale']}")
            email_lines.append(f"   Recommendation: {issue['recommendation']}")
            email_lines.append("")

        email_content = "\n".join(email_lines)
        # Save to output file
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(email_content)
        print(f"Summary email saved to {self.output_file}")
        return email_content


# Example usage
if __name__ == "__main__":
    agent = PlannerAgent()
    agent.generate_summary_email_from_analysis()
    # agent.create_signing_ics_from_intake()
