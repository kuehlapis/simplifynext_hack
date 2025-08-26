from server.service.ocr_service import OCRService
from server.agents.intake_agent import IntakeAgent
from server.agents.analyser_agent import AnalyserAgent 
from server.agents.planner_agent import PlannerAgent
import os
import json


file_name = os.path.abspath("server/contracts/messed_up_rental_agreement_long.pdf")
with open( file_name, "rb") as f:
    pdf_bytes = f.read()

markdown = OCRService.pdf_to_markdown(pdf_bytes, file_name)

intake_agent = IntakeAgent()
intake_output = intake_agent.normalization(markdown)

analyser_agent = AnalyserAgent()
analysis_result = analyser_agent.analyze(intake_output)

# print(analysis_result)
# print(json.dumps(analysis_result, indent=2, ensure_ascii=False))

# with open("analysis_result.json", "w", encoding="utf-8") as outfile:
#     json.dump(analysis_result, outfile, indent=2, ensure_ascii=False)

#if __name__ == "__main__":
#    agent = PlannerAgent()
#    agent.generate_email_with_gemini()
#    agent.create_signing_ics_from_intake()