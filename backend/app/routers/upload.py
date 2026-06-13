from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    UploadFile,
    File
)

router = APIRouter(
    tags=["Upload"]
)

UPLOAD_DIR = Path("/app/static/uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


@router.post("")
async def upload_image(
    file: UploadFile = File(...)
):
    ext = file.filename.split(".")[-1]

    filename = f"{uuid4()}.{ext}"

    filepath = UPLOAD_DIR / filename

    with open(filepath, "wb") as buffer:
        buffer.write(
            await file.read()
        )

    return {
        "url": f"/static/uploads/{filename}"
    }