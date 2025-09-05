from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from server.controller.upload_controller import router as ocr_router
from server.agents.planner_agent import PlannerAgent
from server.agents.intake_agent import IntakeAgent
from server.agents.analyser_agent import AnalyserAgent
from server.agents.packager import PackagerAgent
from server.agents.packager_v2 import PackagerV2Agent
from server.service.email_service import EmailService
import json
from typing import List, Dict, Any
from pathlib import Path
from starlette.responses import FileResponse, RedirectResponse

app = FastAPI()
intake_agent = IntakeAgent()
analyser_agent = AnalyserAgent()
planner_agent = PlannerAgent()
packager_agent = PackagerAgent()
packager_v2_agent = PackagerV2Agent()
EmailServiceMain = EmailService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ocr_router)
BASE_DIR = Path(__file__).resolve().parent  # server/
OUTPUT_DIR = BASE_DIR / "agents" / "outputs"
DOWNLOAD_DIR = OUTPUT_DIR
ARTIFACTS_DIR = OUTPUT_DIR / "artifacts"
DASHBOARD_PATH = OUTPUT_DIR / "dashboard.json"
ARTIFACTS_DIR = OUTPUT_DIR / "artifacts"


@app.get("/")
async def read_root():
    return {"message": "gaytards"}


@app.post("/analyze")
async def start_analyse(request: Request):
    """
    Analyze a document and return formatted data for the frontend dashboard.
    """

    try:
        # document = (await request.body()).decode("utf-8")
        data = await request.json()  # Parse JSON
        name = data.get("name")
        email = data.get("email")
        document = data.get("markdown")

        if not all([name, email, document]):
            raise HTTPException(
                status_code=400, detail="Missing name, email, or document"
            )
        intake_output = intake_agent.normalization(document)
        analysis_result = analyser_agent.analyze(intake_output)
        planner_output = planner_agent.generate_email_with_gemini()
        ics_output = planner_agent.create_signing_ics_from_intake()

        # Pass planner outputs directly to the packager
        dashboard_data = packager_v2_agent.package_results(
            analysis_result=analysis_result,
            planner_email_output=planner_output,
            ics_file_path=ics_output,
            name=name,
        )

        EmailServiceMain.send_invite(email, planner_output, name)

        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


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


@app.post("/package-dashboard")
def package_dashboard():
    """
    Generate the dashboard.json and artifacts using the PackagerAgent.
    Returns the generated dashboard data.
    """
    try:
        dashboard = packager_agent.run_packaging()
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Artifact helpers and endpoints
OUTPUT_DIR = Path("server/agents/outputs")
DASHBOARD_PATH = OUTPUT_DIR / "dashboard.json"


def _read_dashboard() -> Dict[str, Any]:
    if not DASHBOARD_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="dashboard.json not found. Run /package-dashboard first.",
        )
    try:
        with open(DASHBOARD_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read dashboard.json: {e}"
        )


def _infer_media_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".ics":
        return "text/calendar"
    if suffix == ".json":
        return "application/json"
    if suffix == ".pdf":
        return "application/pdf"
    return "application/octet-stream"


@app.get("/artifacts")
def list_artifacts():
    """Return artifact metadata from dashboard.json."""
    data = _read_dashboard()
    artifacts = data.get("artifacts", [])
    return {"artifacts": artifacts}


def _resolve_local(url: str) -> Path:
    p = Path(url)
    if p.is_absolute():
        return p
    url = url.replace("\\", "/")  # normalize
    if url.startswith("server/"):
        return BASE_DIR.parent / url  # repo-root/server/...
    if url.startswith("agents/"):
        return BASE_DIR / url  # server/agents/...
    # last resort: filename-only in artifacts
    return ARTIFACTS_DIR / p.name


@app.get("/download/{artifact_id}")
def download_artifact(artifact_id: str):
    data = _read_dashboard()
    artifacts: List[Dict[str, Any]] = data.get("artifacts", [])
    artifact = next((a for a in artifacts if a.get("id") == artifact_id), None)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    url = (artifact.get("url") or "").strip()
    if url.startswith(("http://", "https://")):
        return RedirectResponse(url=url, status_code=307)

    local_path = _resolve_local(url)
    if not local_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found at {url}")

    return FileResponse(
        path=str(local_path),
        media_type=_infer_media_type(local_path),
        filename=local_path.name,
    )


@app.get("/download-file/{filename}")
def download_file_by_name(filename: str):
    """
    Download a file directly from the download directory by filename.
    Serves files like frontend_package.json, dashboard.json, etc.
    """
    try:
        file_path = DOWNLOAD_DIR / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {filename} not found")

        media_type = _infer_media_type(file_path)
        return FileResponse(
            path=str(file_path), media_type=media_type, filename=file_path.name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to download file: {e}")


@app.get("/downloads")
def list_download_files():
    """
    List all available files in the download directory.
    """
    try:
        if not DOWNLOAD_DIR.exists():
            return {"files": [], "message": "Download directory not found"}

        files = [
            {
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime,
                "type": file_path.suffix.lstrip(".") if file_path.suffix else "unknown",
            }
            for file_path in DOWNLOAD_DIR.glob("*")
            if file_path.is_file()
        ]

        return {"files": files, "total": len(files)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {e}")


@app.get("/frontend-package")
def get_frontend_package():
    """
    Get the comprehensive frontend package data.
    """
    try:
        frontend_package_path = DOWNLOAD_DIR / "frontend_package.json"
        if not frontend_package_path.exists():
            raise HTTPException(
                status_code=404,
                detail="Frontend package not found. Run the packager first.",
            )

        with open(frontend_package_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to read frontend package: {e}"
        )
