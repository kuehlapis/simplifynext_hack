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
intake_agent.normalization(markdown)

# with open("server/agents/outputs/intake_agent.json", "r", encoding="utf-8") as f:
#     intake_data = json.load(f)

# clauses_json = intake_data["summary"]["content"]

# analyser_agent = AnalyserAgent()
# analysis_result = analyser_agent.analyze(clauses_json)

# print(analysis_result)
# print(json.dumps(analysis_result, indent=2, ensure_ascii=False))

# with open("analysis_result.json", "w", encoding="utf-8") as outfile:
#     json.dump(analysis_result, outfile, indent=2, ensure_ascii=False)

# Test PlannerAgent Gemini email and ICS generation
# planner_agent = PlannerAgent()
# planner_agent.generate_email_with_gemini()
# planner_agent.create_signing_ics_from_intake()