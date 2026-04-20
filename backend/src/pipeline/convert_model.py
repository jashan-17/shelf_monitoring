from pathlib import Path

import tensorflow as tf
from tensorflow.keras.models import load_model


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "backend" / "models"


SOURCE_MODEL_PATH = MODELS_DIR / "model_v2.keras"
OUTPUT_TFLITE_PATH = MODELS_DIR / "model_v2.tflite"


def convert_keras_to_tflite(
    source_model_path: Path = SOURCE_MODEL_PATH,
    output_tflite_path: Path = OUTPUT_TFLITE_PATH,
    optimize: bool = True,
) -> Path:
    model = load_model(source_model_path)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    if optimize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()
    output_tflite_path.write_bytes(tflite_model)

    print(f"TFLite model saved to: {output_tflite_path}")
    return output_tflite_path


if __name__ == "__main__":
    convert_keras_to_tflite()
