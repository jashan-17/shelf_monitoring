import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 8
DATASET_PATH = "data/raw_images"
MODEL_SAVE_PATH = "backend/models/model.keras"

train_data = ImageDataGenerator(rescale = 1./255, validation_split = 0.2)

train_generator = train_data.flow_from_directory(
    DATASET_PATH,
    target_size = IMAGE_SIZE,
    batch_size = BATCH_SIZE,
    class_mode = "categorical",
    subset = "training"
)

val_generator = train_data.flow_from_directory(
    DATASET_PATH,
    target_size = IMAGE_SIZE,
    batch_size = BATCH_SIZE,
    class_mode = "categorical",
    subset = "validation"
)


model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape = (224, 224, 3)),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),

    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(4, activation='softmax')
])


model.compile(
    optimizer="adam",
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)


history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10
)

model.save(MODEL_SAVE_PATH)
print("Model saved")