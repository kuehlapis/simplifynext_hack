from server.service.ocr_service import OCRService
from server.agents.intake_agent import IntakeAgent
import os


file_name = os.path.abspath("202Room-Rental-Agreement.pdf")
with open( file_name, "rb") as f:
    pdf_bytes = f.read()

markdown = OCRService.pdf_to_markdown(pdf_bytes, file_name)

agent = IntakeAgent(document=markdown)
print(agent.text_normalization())

