from io import BytesIO
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import DocumentStream


class OCRService:
    @staticmethod
    def pdf_to_markdown(file_bytes: bytes, filename: str) -> str:
        buf = BytesIO(file_bytes)
        src = DocumentStream(name=filename, stream=buf)
        converter = DocumentConverter()
        result = converter.convert(src)
        markdown = result.document.export_to_markdown()
        return markdown
