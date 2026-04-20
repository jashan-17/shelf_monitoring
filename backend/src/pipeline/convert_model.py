import argparse
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
    optimize: bool = False,
) -> Path:
    print(f"Using TensorFlow {tf.__version__}")
    print(f"Loading model from: {source_model_path}")

    model = load_model(source_model_path)

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
    converter.inference_input_type = tf.float32
    converter.inference_output_type = tf.float32

    if optimize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()
    output_tflite_path.write_bytes(tflite_model)

    print(f"TFLite model saved to: {output_tflite_path}")
    print("Generated a float32 TFLite model for broad interpreter compatibility.")
    return output_tflite_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a Keras model to a compatibility-friendly TFLite model.")
    parser.add_argument(
        "--source",
        type=Path,
        default=SOURCE_MODEL_PATH,
        help="Path to the input .keras or .h5 model.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_TFLITE_PATH,
        help="Path to the output .tflite model.",
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Enable default TFLite optimizations. Leave disabled for maximum compatibility.",
    )
    args = parser.parse_args()

    convert_keras_to_tflite(
        source_model_path=args.source,
        output_tflite_path=args.output,
        optimize=args.optimize,
    )


if __name__ == "__main__":
    main()
