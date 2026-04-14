import os
import json
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image

MODEL_PATH = "/opt/airflow/backend/models/model_v2.keras"
IMAGE_FOLDER = "/opt/airflow/data/raw_images"
OUTPUT_CSV = "/opt/airflow/data/predictions/predictions.csv"

CLASS_NAMES = ["empty", "low", "medium", "full"]
METADATA_PATH = os.path.splitext(MODEL_PATH)[0] + "_metadata.json"


def load_metadata():
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "r", encoding="utf-8") as metadata_file:
            return json.load(metadata_file)
    return {
        "class_names": CLASS_NAMES,
        "preprocess_mode": "rescale_01",
    }

model = load_model(MODEL_PATH)
metadata = load_metadata()
class_names = metadata.get("class_names", CLASS_NAMES)
preprocess_mode = metadata.get("preprocess_mode", "rescale_01")

results = []

for class_folder in os.listdir(IMAGE_FOLDER):
    folder_path = os.path.join(IMAGE_FOLDER, class_folder)

    if not os.path.isdir(folder_path):
        continue

    for img_name in os.listdir(folder_path):
        img_path = os.path.join(folder_path, img_name)

        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)

        if preprocess_mode == "mobilenet_v2":
            img_array = preprocess_input(img_array)
        else:
            img_array = img_array / 255.0

        preds = model.predict(img_array)
        pred_index = np.argmax(preds)
        confidence = float(np.max(preds))

        predicted_label = class_names[pred_index]

        results.append({
            "image_name": img_name,
            "actual_label": class_folder,
            "predicted_label": predicted_label,
            "confidence": confidence
        })

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV, index=False)

    print("Predictions saved")
