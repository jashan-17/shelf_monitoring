import json
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image
import cv2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model

from src.api.config import settings

DEFAULT_CLASS_NAMES = ["empty", "low", "medium", "full"]
DATASET_ROOT = Path(__file__).resolve().parents[4] / "data" / "raw_images"
_MODEL = None
_MODEL_METADATA = None
_HEURISTIC_STATS = None


def get_model_metadata(model_path):
    global _MODEL_METADATA
    if _MODEL_METADATA is not None:
        return _MODEL_METADATA

    metadata_path = Path(model_path).with_name(f"{Path(model_path).stem}_metadata.json")
    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as metadata_file:
            _MODEL_METADATA = json.load(metadata_file)
    else:
        _MODEL_METADATA = {
            "class_names": DEFAULT_CLASS_NAMES,
            "preprocess_mode": "rescale_01",
        }

    return _MODEL_METADATA


def get_model():
    global _MODEL
    if _MODEL is None:
        model_path = settings.model_path
        if not model_path.exists() and settings.fallback_model_path.exists():
            model_path = settings.fallback_model_path
        _MODEL = load_model(model_path)
        get_model_metadata(model_path)
    return _MODEL


def _extract_visual_features(image_rgb):
    image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    image_bgr = cv2.resize(image_bgr, (224, 224))

    hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    saturation = hsv_image[:, :, 1]
    brightness = hsv_image[:, :, 2]
    grayscale = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(grayscale, 80, 160)

    return np.array(
        [
            float((saturation > 45).mean()),
            float((brightness > 80).mean()),
            float((edges > 0).mean()),
            float(((saturation < 35) & (brightness < 90)).mean()),
        ],
        dtype=np.float32,
    )


def _compute_occupancy_score(feature_vector):
    saturation_ratio, brightness_ratio, edge_ratio, dark_neutral_ratio = feature_vector
    return float(
        (0.5 * saturation_ratio)
        + (0.4 * edge_ratio)
        + (0.1 * brightness_ratio)
        - (0.3 * dark_neutral_ratio)
    )


def _load_training_heuristics():
    global _HEURISTIC_STATS
    if _HEURISTIC_STATS is not None:
        return _HEURISTIC_STATS

    label_features = {}
    valid_suffixes = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

    if not DATASET_ROOT.exists():
        _HEURISTIC_STATS = {}
        return _HEURISTIC_STATS

    for label in DEFAULT_CLASS_NAMES:
        class_dir = DATASET_ROOT / label
        if not class_dir.exists():
            continue

        features = []
        for image_path in class_dir.iterdir():
            if image_path.suffix.lower() not in valid_suffixes:
                continue

            image = cv2.imread(str(image_path))
            if image is None:
                continue

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            features.append(_extract_visual_features(image_rgb))

        if features:
            feature_array = np.vstack(features)
            occupancy_scores = np.array(
                [_compute_occupancy_score(feature_vector) for feature_vector in feature_array],
                dtype=np.float32,
            )
            label_features[label] = {
                "mean": feature_array.mean(axis=0),
                "std": np.clip(feature_array.std(axis=0), 1e-3, None),
                "occupancy_mean": float(occupancy_scores.mean()),
                "occupancy_std": float(max(occupancy_scores.std(), 1e-3)),
            }

    _HEURISTIC_STATS = label_features
    return _HEURISTIC_STATS


def _predict_with_heuristic(image_rgb):
    heuristic_stats = _load_training_heuristics()
    if not heuristic_stats:
        return {label: 0.25 for label in DEFAULT_CLASS_NAMES}

    image_features = _extract_visual_features(image_rgb)
    occupancy_score = _compute_occupancy_score(image_features)
    occupancy_means = {
        label: heuristic_stats[label]["occupancy_mean"]
        for label in DEFAULT_CLASS_NAMES
        if label in heuristic_stats
    }

    if len(occupancy_means) != len(DEFAULT_CLASS_NAMES):
        return {label: 0.25 for label in DEFAULT_CLASS_NAMES}

    empty_mean = occupancy_means["empty"]
    low_mean = occupancy_means["low"]
    medium_mean = occupancy_means["medium"]
    full_mean = occupancy_means["full"]

    probabilities = {label: 0.0 for label in DEFAULT_CLASS_NAMES}

    if occupancy_score <= empty_mean:
        probabilities["empty"] = 1.0
        return probabilities

    if occupancy_score >= full_mean:
        probabilities["full"] = 1.0
        return probabilities

    if occupancy_score < low_mean:
        ratio = (occupancy_score - empty_mean) / max(low_mean - empty_mean, 1e-6)
        probabilities["empty"] = float(1.0 - ratio)
        probabilities["low"] = float(ratio)
        return probabilities

    if occupancy_score < medium_mean:
        ratio = (occupancy_score - low_mean) / max(medium_mean - low_mean, 1e-6)
        probabilities["low"] = float(1.0 - ratio)
        probabilities["medium"] = float(ratio)
        return probabilities

    ratio = (occupancy_score - medium_mean) / max(full_mean - medium_mean, 1e-6)
    probabilities["medium"] = float(1.0 - ratio)
    probabilities["full"] = float(ratio)
    return probabilities


def _predict_with_model(image_rgb):
    image_array = np.asarray(Image.fromarray(image_rgb).resize((224, 224)), dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)

    model = get_model()
    metadata = _MODEL_METADATA or {
        "class_names": DEFAULT_CLASS_NAMES,
        "preprocess_mode": "rescale_01",
    }
    class_names = metadata.get("class_names", DEFAULT_CLASS_NAMES)
    preprocess_mode = metadata.get("preprocess_mode", "rescale_01")

    if preprocess_mode == "mobilenet_v2":
        image_array = preprocess_input(image_array)
    else:
        image_array = image_array / 255.0

    predictions = model.predict(image_array, verbose=0)[0]
    return {
        label: float(score)
        for label, score in zip(class_names, predictions)
    }


def _normalize_probabilities(probabilities):
    normalized = {label: float(probabilities.get(label, 0.0)) for label in DEFAULT_CLASS_NAMES}
    total = sum(normalized.values())
    if total <= 0:
        return {label: 1.0 / len(DEFAULT_CLASS_NAMES) for label in DEFAULT_CLASS_NAMES}
    return {
        label: normalized[label] / total
        for label in DEFAULT_CLASS_NAMES
    }


def _blend_probabilities(model_probabilities, heuristic_probabilities):
    model_probabilities = _normalize_probabilities(model_probabilities)
    heuristic_probabilities = _normalize_probabilities(heuristic_probabilities)

    model_label = max(model_probabilities, key=model_probabilities.get)
    heuristic_label = max(heuristic_probabilities, key=heuristic_probabilities.get)

    model_weight = 0.55
    heuristic_weight = 0.45

    if heuristic_label in {"empty", "full"} and heuristic_probabilities[heuristic_label] >= 0.95:
        model_weight = 0.02
        heuristic_weight = 0.98
    elif (
        model_label in {"low", "medium"}
        and heuristic_label in {"empty", "full"}
        and heuristic_probabilities[heuristic_label] >= 0.4
    ):
        model_weight = 0.02
        heuristic_weight = 0.98

    blended = {
        label: (model_weight * model_probabilities[label]) + (heuristic_weight * heuristic_probabilities[label])
        for label in DEFAULT_CLASS_NAMES
    }
    return _normalize_probabilities(blended)


def predict_image_bytes(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    image_rgb = np.asarray(image, dtype=np.uint8)

    model_probabilities = _predict_with_model(image_rgb)
    heuristic_probabilities = _predict_with_heuristic(image_rgb)
    final_probabilities = _blend_probabilities(model_probabilities, heuristic_probabilities)

    predicted_label = max(final_probabilities, key=final_probabilities.get)
    confidence = final_probabilities[predicted_label]

    return {
        "predicted_label": predicted_label,
        "confidence": round(float(confidence), 4),
        "probabilities": {
            label: round(float(final_probabilities[label]), 4)
            for label in DEFAULT_CLASS_NAMES
        },
    }
