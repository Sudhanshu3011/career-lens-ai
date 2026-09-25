from fastapi import HTTPException, UploadFile

MAX_FILE_SIZE_MB = 5


def validate_pdf(file: UploadFile, data: bytes) -> None:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid content type. Only PDF files are accepted.",
        )

    if not data.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted PDF file.",
        )

    if len(data) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB} MB.",
        )
