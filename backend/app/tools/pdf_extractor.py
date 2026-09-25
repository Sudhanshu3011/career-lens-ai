import io
import pdfplumber
from app.core.logger import get_logger

logger = get_logger(__name__)


def extract_text(pdf_bytes: bytes) -> str:
    """Direct call for use inside agents."""
    try:
        text_parts = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text.strip())
        if not text_parts:
            raise ValueError("No extractable text found in the PDF.")
        return "\n\n".join(text_parts)
    except Exception as exc:
        logger.exception("PDF extraction failed")
        raise exc
