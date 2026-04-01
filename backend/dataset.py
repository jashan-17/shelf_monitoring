import os
import random
import shutil


# Use a fixed seed so the same split happens each time.
random.seed(42)


# Dataset classes.
CLASSES = ["empty", "low", "medium", "full"]


# Only these image files will be processed.
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


# Split ratios.
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15


def get_paths():
    """
    Build paths from the location of this Python file.

    This is safer than plain relative paths because the script still works
    even if you run it from a different folder.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(script_dir, "dataset")

    train_dir = os.path.join(dataset_dir, "train")
    val_dir = os.path.join(dataset_dir, "val")
    test_dir = os.path.join(dataset_dir, "test")

    return train_dir, val_dir, test_dir


def create_class_folders(base_folder):
    """Create one folder per class."""
    os.makedirs(base_folder, exist_ok=True)

    for class_name in CLASSES:
        os.makedirs(os.path.join(base_folder, class_name), exist_ok=True)


def clear_folder(base_folder):
    """Remove all files inside one split folder."""
    if not os.path.exists(base_folder):
        return

    for class_name in CLASSES:
        class_folder = os.path.join(base_folder, class_name)

        if not os.path.exists(class_folder):
            continue

        for file_name in os.listdir(class_folder):
            file_path = os.path.join(class_folder, file_name)

            if os.path.isfile(file_path):
                os.remove(file_path)


def get_image_files(folder_path):
    """Return only valid image files."""
    if not os.path.exists(folder_path):
        return []

    return [
        file_name
        for file_name in os.listdir(folder_path)
        if file_name.lower().endswith(IMAGE_EXTENSIONS)
        and os.path.isfile(os.path.join(folder_path, file_name))
    ]


def move_files(file_names, source_folder, destination_folder):
    """Move selected files from source to destination."""
    for file_name in file_names:
        source_path = os.path.join(source_folder, file_name)
        destination_path = os.path.join(destination_folder, file_name)
        shutil.move(source_path, destination_path)


def split_one_class(class_name, train_dir, val_dir, test_dir):
    """
    Split one class by moving some images out of train.

    Result:
    - 70% stay in train
    - 15% move to val
    - 15% move to test
    """
    train_class_folder = os.path.join(train_dir, class_name)

    if not os.path.exists(train_class_folder):
        print(f"Skipping '{class_name}' because folder was not found: {train_class_folder}")
        return

    images = get_image_files(train_class_folder)
    random.shuffle(images)

    total_images = len(images)
    train_count = int(total_images * TRAIN_RATIO)
    val_count = int(total_images * VAL_RATIO)
    test_count = total_images - train_count - val_count

    train_files = images[:train_count]
    val_files = images[train_count:train_count + val_count]
    test_files = images[train_count + val_count:]

    # Files in train_files stay where they are.
    move_files(val_files, train_class_folder, os.path.join(val_dir, class_name))
    move_files(test_files, train_class_folder, os.path.join(test_dir, class_name))

    print(
        f"{class_name}: {total_images} images -> "
        f"{len(train_files)} train, "
        f"{len(val_files)} val, "
        f"{len(test_files)} test"
    )


def main():
    """
    Why the old FileNotFoundError happened:
    The previous code searched for dataset/raw/empty, dataset/raw/low, and so on.
    But your dataset is already inside dataset/train/empty, dataset/train/low,
    dataset/train/medium, and dataset/train/full.
    Since dataset/raw did not exist, Python raised FileNotFoundError.

    How relative paths work in Python:
    A relative path like "dataset/train" is resolved from the current working
    directory, which is usually the folder where you run the command.

    Example:
    If you run the script inside the backend folder, then "dataset/train"
    means backend/dataset/train

    If you run the script from somewhere else, that same relative path may
    point to a different place.

    This script uses __file__ so the paths are built from the location of
    this Python file itself.
    """
    train_dir, val_dir, test_dir = get_paths()

    if not os.path.exists(train_dir):
        print(f"Source folder not found: {train_dir}")
        return

    print("Source folder:", train_dir)
    print("Creating val and test folders...")

    create_class_folders(val_dir)
    create_class_folders(test_dir)

    print("Clearing old val and test files...")
    clear_folder(val_dir)
    clear_folder(test_dir)

    print("\nStarting dataset split...\n")

    for class_name in CLASSES:
        split_one_class(
            class_name=class_name,
            train_dir=train_dir,
            val_dir=val_dir,
            test_dir=test_dir,
        )

    print("\nDataset split completed successfully.")
    print("Final folders: dataset/train, dataset/val, dataset/test")
    print("No extra backup folder is created.")


if __name__ == "__main__":
    main()
