from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.responses import PlainTextResponse

from server.service.ocr_service import OCRService

router = APIRouter()


@router.post("/convert", response_class=PlainTextResponse)
async def convert_pdf_to_markdown(file: UploadFile = File(...)):
    filename = file.filename or "upload.pdf"
    content_type = file.content_type or ""
    if not (filename.lower().endswith(".pdf") or content_type == "application/pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")
    try:
        raw = await file.read()
        markdown = OCRService.pdf_to_markdown(raw, filename)
        return PlainTextResponse(markdown, media_type="text/markdown; charset=utf-8")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Conversion failed: {type(e).__name__}: {e}"
        )
