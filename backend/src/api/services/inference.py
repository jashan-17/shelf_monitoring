import json
import logging
import threading
from pathlib import Path
from typing import BinaryIO

import numpy as np
from PIL import Image, UnidentifiedImageError
from tflite_runtime.interpreter import Interpreter

from src.api.config import settings

logger = logging.getLogger(__name__)

DEFAULT_CLASS_NAMES = ["empty", "low", "medium", "full"]
IMAGE_SIZE = (224, 224)


class ModelUnavailableError(RuntimeError):
    pass


class InvalidImageError(RuntimeError):
    pass


class TFLiteModelService:
    def __init__(self) -> None:
        self._interpreter: Interpreter | None = None
        self._input_details: list[dict] | None = None
        self._output_details: list[dict] | None = None
        self._metadata = {
            "class_names": DEFAULT_CLASS_NAMES,
            "preprocess_mode": "rescale_01",
        }
        self._active_model_path: Path | None = None
        self._load_error: str | None = None
        self._load_attempted = False
        self._load_lock = threading.Lock()
        self._predict_lock = threading.Lock()

    def preload(self) -> bool:
        return self._ensure_model_loaded(raise_on_failure=False)

    def _candidate_model_paths(self) -> list[Path]:
        candidates = [settings.model_path]
        if settings.fallback_model_path != settings.model_path:
            candidates.append(settings.fallback_model_path)
        return candidates

    def _missing_model_message(self) -> str:
        attempted_paths = [str(path) for path in self._candidate_model_paths()]
        return (
            "TFLite model file not found. "
            f"Expected one of: {', '.join(attempted_paths)}. "
            "Generate the model with backend/src/pipeline/convert_model.py "
            "and commit the resulting .tflite file to the repository."
        )

    def _load_metadata(self, model_path: Path) -> dict:
        metadata_path = model_path.with_name(f"{model_path.stem}_metadata.json")
        if metadata_path.exists():
            with metadata_path.open("r", encoding="utf-8") as metadata_file:
                return json.load(metadata_file)
        return {
            "class_names": DEFAULT_CLASS_NAMES,
            "preprocess_mode": "rescale_01",
        }

    def _load_interpreter(self, model_path: Path) -> Interpreter:
        interpreter = Interpreter(model_path=str(model_path), num_threads=1)
        interpreter.allocate_tensors()
        return interpreter

    def _ensure_model_loaded(self, *, raise_on_failure: bool) -> bool:
        if self._interpreter is not None:
            return True

        with self._load_lock:
            if self._interpreter is not None:
                return True
            if self._load_attempted and self._interpreter is None:
                if raise_on_failure:
                    raise ModelUnavailableError(self._load_error or "TFLite model could not be loaded.")
                return False

            self._load_attempted = True
            errors: list[str] = []

            for model_path in self._candidate_model_paths():
                if not model_path.exists():
                    errors.append(f"{model_path}: file not found")
                    continue

                try:
                    logger.info("Loading TFLite model from %s", model_path)
                    interpreter = self._load_interpreter(model_path)
                    self._interpreter = interpreter
                    self._input_details = interpreter.get_input_details()
                    self._output_details = interpreter.get_output_details()
                    self._metadata = self._load_metadata(model_path)
                    self._active_model_path = model_path
                    self._load_error = None
                    logger.info("TFLite model loaded from %s", model_path)
                    return True
                except Exception as exc:
                    logger.exception("Failed to load TFLite model from %s", model_path)
                    errors.append(f"{model_path}: {exc}")

            self._load_error = " ; ".join(errors) if errors else self._missing_model_message()

            if all(not model_path.exists() for model_path in self._candidate_model_paths()):
                self._load_error = self._missing_model_message()

        if raise_on_failure:
            raise ModelUnavailableError(self._load_error)
        return False

    def _prepare_image_batch(self, image_file: BinaryIO) -> np.ndarray:
        try:
            image_file.seek(0)
            with Image.open(image_file) as image:
                image = image.convert("RGB")
                image = image.resize(IMAGE_SIZE)
                image_array = np.asarray(image, dtype=np.float32)
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError("Unable to read the uploaded image.") from exc
        finally:
            try:
                image_file.seek(0)
            except Exception:
                pass

        image_array /= 255.0
        return np.expand_dims(image_array, axis=0)

    def predict(self, image_file: BinaryIO) -> dict[str, float | dict[str, float]]:
        self._ensure_model_loaded(raise_on_failure=True)

        assert self._interpreter is not None
        assert self._input_details is not None
        assert self._output_details is not None

        input_data = self._prepare_image_batch(image_file)
        input_detail = self._input_details[0]
        output_detail = self._output_details[0]

        if input_detail["dtype"] != np.float32:
            input_data = input_data.astype(input_detail["dtype"])

        try:
            with self._predict_lock:
                self._interpreter.set_tensor(input_detail["index"], input_data)
                self._interpreter.invoke()
                predictions = self._interpreter.get_tensor(output_detail["index"])[0]
        finally:
            del input_data

        class_names = self._metadata.get("class_names", DEFAULT_CLASS_NAMES)
        probabilities = {
            label: float(score)
            for label, score in zip(class_names, predictions)
        }

        predicted_label = max(probabilities, key=probabilities.get)
        confidence = probabilities[predicted_label]

        return {
            "predicted_label": predicted_label,
            "confidence": round(float(confidence), 4),
            "probabilities": {label: round(float(score), 4) for label, score in probabilities.items()},
        }


_MODEL_SERVICE = TFLiteModelService()


def preload_model() -> bool:
    return _MODEL_SERVICE.preload()


def predict_upload_file(image_file: BinaryIO) -> dict[str, float | dict[str, float]]:
    return _MODEL_SERVICE.predict(image_file)
