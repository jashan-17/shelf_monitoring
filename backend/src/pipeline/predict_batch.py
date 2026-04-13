import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

MODEL_PATH = "backend/models/model.keras"
IMAGE_FOLDER = "data/raw_images"
OUTPUT_CSV = "data/predictions/predictions.csv"

CLASS_NAMES = ["empty", "low", "medium", "full"]

model = load_model(MODEL_PATH)

results = []

for class_folder in os.listdir(IMAGE_FOLDER):
    folder_path = os.path.join(IMAGE_FOLDER, class_folder)

    if not os.path.isdir(folder_path):
        continue

    for img_name in os.listdir(folder_path):
        img_path = os.path.join(folder_path, img_name)

        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        preds = model.predict(img_array)
        pred_index = np.argmax(preds)
        confidence = float(np.max(preds))

        predicted_label = CLASS_NAMES[pred_index]

        results.append({
            "image_name": img_name,
            "actual_label": class_folder,
            "predicted_label": predicted_label,
            "confidence": confidence
        })

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV, index=False)

    print("Predictions saved")