import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras import callbacks, layers, models, optimizers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from dataset_utils import (
    build_tf_dataset,
    count_labels,
    discover_class_names,
    scan_valid_images,
    stratified_split,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = PROJECT_ROOT / "data" / "raw_images"
MODEL_OUTPUT_PATH = PROJECT_ROOT / "backend" / "models" / "model_v2.keras"
HISTORY_OUTPUT_PATH = PROJECT_ROOT / "backend" / "models" / "model_v2_history.json"
REPORT_OUTPUT_PATH = PROJECT_ROOT / "backend" / "models" / "model_v2_classification_report.txt"
CONFUSION_MATRIX_OUTPUT_PATH = PROJECT_ROOT / "backend" / "models" / "model_v2_confusion_matrix.csv"
METADATA_OUTPUT_PATH = PROJECT_ROOT / "backend" / "models" / "model_v2_metadata.json"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 16
VALIDATION_SPLIT = 0.2
SEED = 42
INITIAL_EPOCHS = 10
FINE_TUNE_EPOCHS = 5
FINE_TUNE_AT = 100


def build_datasets():
    class_names = discover_class_names(DATASET_PATH)
    file_paths, labels, class_names, bad_files = scan_valid_images(
        DATASET_PATH,
        image_size=IMAGE_SIZE,
        class_names=class_names,
    )

    print("\nClass names discovered by Keras:")
    print(class_names)
    print("\nClass indices:")
    print({name: index for index, name in enumerate(class_names)})

    if bad_files:
        print("\nSkipped unreadable image files:")
        for item in bad_files:
            print(f"- {item['path']}")

    print(f"\nValid image files used for training: {len(file_paths)}")

    train_paths, val_paths, train_labels, val_labels = stratified_split(
        file_paths=file_paths,
        labels=labels,
        validation_split=VALIDATION_SPLIT,
        seed=SEED,
    )

    train_dataset = build_tf_dataset(
        file_paths=train_paths,
        labels=train_labels,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        training=True,
    )
    validation_dataset = build_tf_dataset(
        file_paths=val_paths,
        labels=val_labels,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        training=False,
    )

    return train_dataset, validation_dataset, class_names, train_labels, val_labels


def get_data_augmentation():
    return tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.08),
            layers.RandomZoom(0.12),
            layers.RandomTranslation(height_factor=0.08, width_factor=0.08),
            layers.RandomContrast(0.1),
        ],
        name="data_augmentation",
    )


def build_model(num_classes):
    data_augmentation = get_data_augmentation()

    base_model = MobileNetV2(
        input_shape=IMAGE_SIZE + (3,),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = layers.Input(shape=IMAGE_SIZE + (3,))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs)
    return model, base_model


def compile_model(model, learning_rate):
    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )


def get_callbacks():
    return [
        callbacks.ModelCheckpoint(
            filepath=MODEL_OUTPUT_PATH,
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
            verbose=1,
        ),
        callbacks.EarlyStopping(
            monitor="val_loss",
            patience=4,
            restore_best_weights=True,
            verbose=1,
        ),
    ]


def compute_class_weights_from_training_labels(train_labels, class_names):
    print("\nTraining split class distribution:")
    print(count_labels(train_labels, class_names))

    label_array = np.array(train_labels, dtype=np.int32)
    unique_labels = np.unique(label_array)
    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=unique_labels,
        y=label_array,
    )
    return {int(label): float(weight) for label, weight in zip(unique_labels, class_weights)}


def merge_history(initial_history, fine_tune_history=None):
    merged_history = {key: list(values) for key, values in initial_history.history.items()}

    if fine_tune_history is not None:
        for key, values in fine_tune_history.history.items():
            merged_history.setdefault(key, [])
            merged_history[key].extend(values)

    return merged_history


def save_history(history_dict):
    with open(HISTORY_OUTPUT_PATH, "w", encoding="utf-8") as history_file:
        json.dump(history_dict, history_file, indent=2)


def save_metadata(class_names):
    metadata = {
        "class_names": class_names,
        "image_size": list(IMAGE_SIZE),
        "preprocess_mode": "mobilenet_v2",
        "architecture": "MobileNetV2",
    }
    with open(METADATA_OUTPUT_PATH, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)


def save_classification_report(report_dict):
    with open(REPORT_OUTPUT_PATH, "w", encoding="utf-8") as report_file:
        for label, metrics in report_dict.items():
            report_file.write(f"{label}: {metrics}\n")


def save_confusion_matrix(matrix, class_names):
    with open(CONFUSION_MATRIX_OUTPUT_PATH, "w", encoding="utf-8") as matrix_file:
        header = ",".join(["actual/predicted"] + class_names)
        matrix_file.write(header + "\n")
        for class_name, row in zip(class_names, matrix):
            matrix_file.write(",".join([class_name] + [str(value) for value in row]) + "\n")


def evaluate_model(model, validation_dataset, class_names):
    validation_loss, validation_accuracy = model.evaluate(validation_dataset, verbose=1)

    true_labels = []
    predicted_labels = []

    for images, labels in validation_dataset:
        predictions = model.predict(images, verbose=0)
        true_labels.extend(labels.numpy())
        predicted_labels.extend(np.argmax(predictions, axis=1))

    report = classification_report(
        true_labels,
        predicted_labels,
        labels=list(range(len(class_names))),
        target_names=class_names,
        digits=4,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(
        true_labels,
        predicted_labels,
        labels=list(range(len(class_names))),
    )

    print("\nValidation accuracy:")
    print(f"{validation_accuracy:.4f}")
    print("\nClassification report:")
    print(
        classification_report(
            true_labels,
            predicted_labels,
            labels=list(range(len(class_names))),
            target_names=class_names,
            digits=4,
            zero_division=0,
        )
    )
    print("Confusion matrix:")
    print(matrix)

    save_classification_report(report)
    save_confusion_matrix(matrix, class_names)

    return validation_loss, validation_accuracy


def train():
    tf.random.set_seed(SEED)
    np.random.seed(SEED)

    print("Dataset path:")
    print(DATASET_PATH)

    class_names = discover_class_names(DATASET_PATH)
    file_paths, labels, _, bad_files = scan_valid_images(
        DATASET_PATH,
        image_size=IMAGE_SIZE,
        class_names=class_names,
    )

    print("\nImage count by class:")
    print(count_labels(labels, class_names))

    if bad_files:
        print("\nSkipped unreadable image files:")
        for item in bad_files:
            print(f"- {item['path']}")

    train_dataset, validation_dataset, class_names, train_labels, val_labels = build_datasets()

    print("\nValidation split class distribution:")
    print(count_labels(val_labels, class_names))

    class_weights = compute_class_weights_from_training_labels(train_labels, class_names)
    print("\nComputed class weights:")
    print(class_weights)

    model, base_model = build_model(num_classes=len(class_names))
    compile_model(model, learning_rate=1e-3)

    print("\nStarting stage 1 training with frozen MobileNetV2 base...")
    initial_history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=INITIAL_EPOCHS,
        callbacks=get_callbacks(),
        class_weight=class_weights,
        verbose=1,
    )

    print("\nStarting stage 2 fine-tuning...")
    base_model.trainable = True
    for layer in base_model.layers[:FINE_TUNE_AT]:
        layer.trainable = False

    compile_model(model, learning_rate=1e-5)

    fine_tune_history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=INITIAL_EPOCHS + FINE_TUNE_EPOCHS,
        initial_epoch=initial_history.epoch[-1] + 1,
        callbacks=get_callbacks(),
        class_weight=class_weights,
        verbose=1,
    )

    combined_history = merge_history(initial_history, fine_tune_history)
    save_history(combined_history)
    save_metadata(class_names)

    best_model = tf.keras.models.load_model(MODEL_OUTPUT_PATH)
    validation_loss, validation_accuracy = evaluate_model(
        best_model,
        validation_dataset,
        class_names,
    )

    train_accuracy = max(combined_history.get("accuracy", [0.0]))
    best_val_accuracy = max(combined_history.get("val_accuracy", [0.0]))

    print("\nTraining summary:")
    print(f"Best training accuracy: {train_accuracy:.4f}")
    print(f"Best validation accuracy: {best_val_accuracy:.4f}")
    print(f"Final evaluated validation accuracy: {validation_accuracy:.4f}")
    print(f"Final evaluated validation loss: {validation_loss:.4f}")
    print(f"\nBest model saved to: {MODEL_OUTPUT_PATH}")
    print(f"Model metadata saved to: {METADATA_OUTPUT_PATH}")
    print(f"Training history saved to: {HISTORY_OUTPUT_PATH}")
    print(f"Classification report saved to: {REPORT_OUTPUT_PATH}")
    print(f"Confusion matrix saved to: {CONFUSION_MATRIX_OUTPUT_PATH}")


if __name__ == "__main__":
    train()
