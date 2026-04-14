from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

from dataset_utils import (
    build_tf_dataset,
    discover_class_names,
    scan_valid_images,
    stratified_split,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = PROJECT_ROOT / "data" / "raw_images"
MODELS_DIR = PROJECT_ROOT / "backend" / "models"

MODEL_PATHS = {
    "model_v1": MODELS_DIR / "model.keras",
    "model_v2": MODELS_DIR / "model_v2.keras",
}

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
VALIDATION_SPLIT = 0.2
SEED = 42


def build_validation_dataset():
    class_names = discover_class_names(DATASET_PATH)
    file_paths, labels, class_names, bad_files = scan_valid_images(
        DATASET_PATH,
        image_size=IMAGE_SIZE,
        class_names=class_names,
    )

    if bad_files:
        print("\nSkipped unreadable image files:")
        for item in bad_files:
            print(f"- {item['path']}")

    _, val_paths, _, val_labels = stratified_split(
        file_paths=file_paths,
        labels=labels,
        validation_split=VALIDATION_SPLIT,
        seed=SEED,
    )

    validation_dataset = build_tf_dataset(
        file_paths=val_paths,
        labels=val_labels,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        training=False,
    )
    return validation_dataset, class_names


def evaluate_model(model_name, model_path, validation_dataset, class_names):
    if not model_path.exists():
        print(f"\nSkipping {model_name}: model file not found at {model_path}")
        return None

    print(f"\nEvaluating {model_name}")
    print(f"Model path: {model_path}")

    model = tf.keras.models.load_model(model_path)

    true_labels = []
    predicted_labels = []

    for images, labels in validation_dataset:
        model_input = tf.cast(images, tf.float32)

        if model_name == "model_v2":
            predictions = model.predict(model_input, verbose=0)
        else:
            predictions = model.predict(model_input / 255.0, verbose=0)

        true_labels.extend(labels.numpy())
        predicted_labels.extend(np.argmax(predictions, axis=1))

    accuracy = float(np.mean(np.array(true_labels) == np.array(predicted_labels)))
    report = classification_report(
        true_labels,
        predicted_labels,
        labels=list(range(len(class_names))),
        target_names=class_names,
        digits=4,
        zero_division=0,
    )
    matrix = confusion_matrix(
        true_labels,
        predicted_labels,
        labels=list(range(len(class_names))),
    )

    print(f"Validation accuracy: {accuracy:.4f}")
    print("\nClassification report:")
    print(report)
    print("Confusion matrix:")
    print(matrix)

    return {
        "model_name": model_name,
        "accuracy": accuracy,
        "confusion_matrix": matrix,
    }


def compare_results(results):
    valid_results = [result for result in results if result is not None]
    if len(valid_results) < 2:
        return

    print("\nComparison summary:")
    for result in valid_results:
        print(f"- {result['model_name']}: {result['accuracy']:.4f}")

    best_result = max(valid_results, key=lambda item: item["accuracy"])
    print(f"\nBest validation accuracy: {best_result['model_name']} ({best_result['accuracy']:.4f})")


def main():
    print("Building shared validation dataset...")
    validation_dataset, class_names = build_validation_dataset()

    print("\nClass names:")
    print(class_names)

    results = []
    for model_name, model_path in MODEL_PATHS.items():
        results.append(evaluate_model(model_name, model_path, validation_dataset, class_names))

    compare_results(results)


if __name__ == "__main__":
    main()
