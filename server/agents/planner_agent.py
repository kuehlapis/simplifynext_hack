import json


class PlannerAgent:
    def __init__(self):
        self.output_file = "planner-agent.json"

    def generate_planner_data(self, pdf_data):
        """
        Generate planner data based on inputs from the PDF decoding agent.
        :param pdf_data: Data extracted from the PDF decoding agent.
        """
        # Example structure for planner data
        planner_data = {
            "negotiation_email": {
                "draft": "Please review the attached rider clauses.",
                "tone_options": ["firm", "courteous", "neutral"],
            },
            "rider_clauses": {
                "clause_1": "Concrete clause edit example 1",
                "clause_2": "Concrete clause edit example 2",
            },
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
