from fastapi import APIRouter, File, HTTPException, UploadFile

from src.api.schemas.responses import PredictionResult
from src.api.services.inference import predict_upload_file

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictionResult)
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size <= 0:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    prediction = predict_upload_file(file.file)

    return {
        "image_name": file.filename or "uploaded-image",
        **prediction,
        "saved_to_database": False,
    }
