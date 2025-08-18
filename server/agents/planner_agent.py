import json


class PlannerAgent:
    def __init__(self, rules_file="planner_agent_rules.json"):
        with open(rules_file, "r") as file:
            self.rules = json.load(file)
        self.output_file = "planner-agent.json"

    def generate_planner_data(self, pdf_data):
        """
        Generate planner data based on inputs from the PDF decoding agent and rules.
        :param pdf_data: Data extracted from the PDF decoding agent.
        """
        planner_data = {
            "negotiation_email": {
                "draft": self.rules["negotiation_email"]["email_template"],
                "tone_options": self.rules["negotiation_email"]["tone_options"],
            },
            "rider_clauses": self.rules["rider_clauses"],
        }

        # Write planner data to JSON file
        with open(self.output_file, "w") as file:
            json.dump(planner_data, file, indent=4)

        return planner_data


# Example usage
if __name__ == "__main__":
    agent = PlannerAgent()
    pdf_data = {}  # Replace with actual PDF data from the decoding agent
    agent.generate_planner_data(pdf_data)
