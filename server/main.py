from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from server.controller.upload_controller import router as ocr_router
from server.agents.planner_agent import PlannerAgent
from server.agents.intake_agent import IntakeAgent
from server.agents.analyser_agent import AnalyserAgent
import json

app = FastAPI()
intake_agent = IntakeAgent()
analyser_agent = AnalyserAgent()
planner_agent = PlannerAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ocr_router)


@app.get("/")
async def read_root():
    return {"message": "gaytards"}


@app.get("/analyze")
async def start_analyse(document: str):
    intake_output = intake_agent.normalization(document)

    analysis_result = analyser_agent.analyze(intake_output)

    planner_output = planner_agent.generate_email_with_gemini(analysis_result)

    return planner_output, analysis_result


@app.post("/generate-planner-data")
def generate_planner_data(pdf_data: dict):
    """
    Generate planner data using the planner agent.
    :param pdf_data: Parsed PDF data.
    """
    try:
        planner_data = planner_agent.generate_planner_data(pdf_data)
        return {"message": "Planner data generated successfully", "data": planner_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fetch-planner-data")
def fetch_planner_data():
    """
    Fetch the contents of planner-agent.json.
    """
    try:
        with open(planner_agent.output_file, "r") as file:
            planner_data = json.load(file)
        return planner_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Planner data not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/update-planner-data")
def update_planner_data(updated_data: dict):
    """
    Update the planner data in planner-agent.json.
    :param updated_data: New planner data.
    """
    try:
        with open(planner_agent.output_file, "w") as file:
            json.dump(updated_data, file, indent=4)
        return {"message": "Planner data updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
