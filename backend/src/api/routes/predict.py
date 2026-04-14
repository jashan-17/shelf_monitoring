from fastapi import APIRouter, File, HTTPException, UploadFile

from src.api.schemas.responses import PredictionResult
from src.api.services.inference import predict_image_bytes

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictionResult)
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")

    prediction = predict_image_bytes(image_bytes)

    return {
        "image_name": file.filename or "uploaded-image",
        **prediction,
        "saved_to_database": False,
    }
