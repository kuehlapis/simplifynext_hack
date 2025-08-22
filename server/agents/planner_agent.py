import json
import re
from datetime import datetime
from ics import Calendar, Event
from server.util.ics_module import ICSModule


class PlannerAgent:
    def suggest_alternative_time(self, event_start: str, event_end: str):
        """
        Use AI to suggest the next available time slot for an event, given current calendar events.
        :param event_start: Proposed start time (string, e.g., '2025-08-18 10:00:00').
        :param event_end: Proposed end time (string).
        :return: Tuple of (new_start, new_end) as strings.
        """
        ics_module = ICSModule()
        events = []
        for event in ics_module.calendar.events:
            events.append(
                {"name": event.name, "start": str(event.begin), "end": str(event.end)}
            )
        prompt = (
            f"Given the following calendar events: {json.dumps(events)}\n"
            f"and a proposed event from {event_start} to {event_end}, "
            "suggest the next available non-conflicting time slot for the event. "
            "Return the new start and end time as a JSON object with 'start' and 'end'."
        )
        response = self.client.generate_content(prompt)
        try:
            match = re.search(r"\{.*\}", response.text, flags=re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in AI output")
            json_str = match.group(0)
            data = json.loads(json_str)
            return data["start"], data["end"]
        except Exception as exc:
            raise ValueError(f"Error parsing AI response for alternative time: {exc}")

    def __init__(self, rules_file="planner_agent_rules.json"):
        import os

        rules_path = os.path.join(os.path.dirname(__file__), rules_file)
        with open(rules_path, "r") as file:
            self.rules = json.load(file)
        self.output_file = "planner-agent.json"
        self.memory = {}

    def generate_planner_data(self, pdf_data):
        """
        Generate planner data based on inputs from the PDF decoding agent and rules.
        :param pdf_data: Data extracted from the PDF decoding agent.
        """
        # Try to read rider clauses from analyser_agent.json
        import os

        rider_clauses = None
        analyser_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "analyser_agent.json"
        )
        try:
            with open(analyser_path, "r", encoding="utf-8") as f:
                analyser_data = json.load(f)
                rider_clauses = analyser_data.get("rider_clauses")
        except Exception:
            pass
        if rider_clauses is None:
            rider_clauses = self.rules["rider_clauses"]

        planner_data = {
            "negotiation_email": {
                "draft": self.rules["negotiation_email"]["email_template"],
                "tone_options": self.rules["negotiation_email"]["tone_options"],
            },
            "rider_clauses": rider_clauses,
        }

        # Write planner data to JSON file
        with open(self.output_file, "w") as file:
            json.dump(planner_data, file, indent=4)

        return planner_data

    def construct_and_send_email(self, email_template: str, tone_options: list):
        # Construct email using template and tone
        email_content = email_template.format(**self.pdf_data)
        self.memory["email"] = {
            "content": email_content,
            "tone_options": tone_options,
        }
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(self.memory["email"], f, indent=2, ensure_ascii=False)
        print(f"Saved email to {self.output_file}")
        return email_content

    def create_ics_file(self, event_title: str, event_start: str, event_end: str):
        # Create ICS calendar event
        try:
            c = Calendar()
            e = Event()
            e.name = event_title
            e.begin = event_start
            e.end = event_end
            c.events.add(e)
            ics_filename = "planner_event.ics"
            with open(ics_filename, "w", encoding="utf-8") as f:
                f.writelines(c)
            self.memory["ics"] = {
                "title": event_title,
                "start": event_start,
                "end": event_end,
                "file": ics_filename,
            }
            print(f"Saved ICS file to {ics_filename}")
            return ics_filename
        except Exception as exc:
            raise ValueError(f"Error creating ICS file: {exc}")


# Example usage - for testing can remove later
if __name__ == "__main__":
    agent = PlannerAgent()
    pdf_data = {}  # Replace with actual PDF data from the decoding agent
    agent.generate_planner_data(pdf_data)

    # Read agreement date from intake_agent.json
    try:
        import os

        intake_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "intake_agent.json"
        )
        with open(intake_path, "r", encoding="utf-8") as f:
            intake_data = json.load(f)
        date_agreed = intake_data["anchor"]["content"]["document"]["agreement"][
            "date_agreed"
        ]
        # Convert date_agreed from DD/MM/YY to YYYY-MM-DD format
        date_obj = datetime.strptime(date_agreed, "%d/%m/%y")
        event_start = date_obj.strftime("%Y-%m-%d") + " 14:00:00"
        event_end = date_obj.strftime("%Y-%m-%d") + " 15:00:00"
        event_title = "Agreement Sign Meeting"
        ics_file = agent.create_ics_file(event_title, event_start, event_end)
        print(f"ICS file created: {ics_file}")
    except Exception as e:
        print(f"Error reading intake_agent.json or creating ICS file: {e}")
