from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
AUTOTUNE = tf.data.AUTOTUNE


def discover_class_names(dataset_path):
    dataset_path = Path(dataset_path)
    return sorted([path.name for path in dataset_path.iterdir() if path.is_dir()])


def scan_valid_images(dataset_path, image_size, class_names=None):
    dataset_path = Path(dataset_path)
    class_names = class_names or discover_class_names(dataset_path)

    file_paths = []
    labels = []
    bad_files = []

    for class_index, class_name in enumerate(class_names):
        class_dir = dataset_path / class_name
        for file_path in sorted(class_dir.iterdir()):
            if not file_path.is_file() or file_path.suffix.lower() not in VALID_EXTENSIONS:
                continue

            try:
                image_bytes = tf.io.read_file(str(file_path))
                decoded = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
                tf.image.resize(decoded, image_size)
                file_paths.append(str(file_path))
                labels.append(class_index)
            except Exception as exc:
                bad_files.append({"path": str(file_path), "error": str(exc)})

    return file_paths, labels, class_names, bad_files


def stratified_split(file_paths, labels, validation_split, seed):
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        file_paths,
        labels,
        test_size=validation_split,
        random_state=seed,
        shuffle=True,
        stratify=labels,
    )
    return train_paths, val_paths, train_labels, val_labels


def decode_and_resize(path, label, image_size):
    image_bytes = tf.io.read_file(path)
    image = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
    image = tf.image.resize(image, image_size)
    image = tf.cast(image, tf.float32)
    return image, label


def build_tf_dataset(file_paths, labels, image_size, batch_size, training):
    dataset = tf.data.Dataset.from_tensor_slices((file_paths, labels))
    if training:
        dataset = dataset.shuffle(buffer_size=len(file_paths), reshuffle_each_iteration=True)

    dataset = dataset.map(
        lambda path, label: decode_and_resize(path, label, image_size),
        num_parallel_calls=AUTOTUNE,
    )
    dataset = dataset.batch(batch_size).prefetch(AUTOTUNE)
    return dataset


def count_labels(labels, class_names):
    counts = {class_name: 0 for class_name in class_names}
    unique_labels, label_counts = np.unique(labels, return_counts=True)
    for label, count in zip(unique_labels, label_counts):
        counts[class_names[int(label)]] = int(count)
    return counts
