import argparse
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = PROJECT_ROOT / "backend" / "models"

SOURCE_MODEL_PATH = MODELS_DIR / "model_v2.keras"
INTERMEDIATE_SAVED_MODEL_PATH = MODELS_DIR / "model_v2_inference_savedmodel"
OUTPUT_TFLITE_PATH = MODELS_DIR / "model_v2.tflite"


def export_inference_saved_model(
    source_model_path: Path = SOURCE_MODEL_PATH,
    output_saved_model_path: Path = INTERMEDIATE_SAVED_MODEL_PATH,
) -> Path:
    import keras

    print(f"Using Keras {keras.__version__}")
    print(f"Loading training model from: {source_model_path}")

    model = keras.models.load_model(source_model_path)
    base_model = model.get_layer("mobilenetv2_1.00_224")
    gap = model.get_layer("global_average_pooling2d")
    dropout = model.get_layer("dropout")
    dense = model.get_layer("dense")

    inputs = keras.Input(shape=(224, 224, 3), dtype="float32", name="image")
    x = base_model(inputs, training=False)
    x = gap(x)
    x = dropout(x, training=False)
    outputs = dense(x)

    inference_model = keras.Model(inputs=inputs, outputs=outputs, name="model_v2_inference")

    if output_saved_model_path.exists():
        import shutil

        shutil.rmtree(output_saved_model_path)

    inference_model.export(output_saved_model_path)
    print(f"Inference SavedModel exported to: {output_saved_model_path}")
    return output_saved_model_path


def convert_saved_model_to_tflite(
    saved_model_path: Path = INTERMEDIATE_SAVED_MODEL_PATH,
    output_tflite_path: Path = OUTPUT_TFLITE_PATH,
    optimize: bool = False,
) -> Path:
    import tensorflow as tf

    print(f"Using TensorFlow {tf.__version__}")
    print(f"Converting SavedModel from: {saved_model_path}")

    converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_path))
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS]
    converter.inference_input_type = tf.float32
    converter.inference_output_type = tf.float32

    if optimize:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()
    output_tflite_path.write_bytes(tflite_model)

    print(f"TFLite model saved to: {output_tflite_path}")
    print("Generated a float32 TFLite model for tflite-runtime 2.14.0 compatibility.")
    return output_tflite_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a Keras 3 training model to an inference-only SavedModel or convert a SavedModel to TFLite."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser(
        "export-inference-savedmodel",
        help="Load the Keras training model and export an inference-only SavedModel without augmentation layers.",
    )
    export_parser.add_argument(
        "--source",
        type=Path,
        default=SOURCE_MODEL_PATH,
        help="Path to the input .keras model.",
    )
    export_parser.add_argument(
        "--output",
        type=Path,
        default=INTERMEDIATE_SAVED_MODEL_PATH,
        help="Path to the output SavedModel directory.",
    )

    convert_parser = subparsers.add_parser(
        "convert-savedmodel",
        help="Convert an inference-only SavedModel to a compatibility-friendly TFLite model.",
    )
    convert_parser.add_argument(
        "--source",
        type=Path,
        default=INTERMEDIATE_SAVED_MODEL_PATH,
        help="Path to the input SavedModel directory.",
    )
    convert_parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_TFLITE_PATH,
        help="Path to the output .tflite model.",
    )
    convert_parser.add_argument(
        "--optimize",
        action="store_true",
        help="Enable default TFLite optimizations. Leave disabled for maximum compatibility.",
    )

    args = parser.parse_args()

    if args.command == "export-inference-savedmodel":
        export_inference_saved_model(
            source_model_path=args.source,
            output_saved_model_path=args.output,
        )
    elif args.command == "convert-savedmodel":
        convert_saved_model_to_tflite(
            saved_model_path=args.source,
            output_tflite_path=args.output,
            optimize=args.optimize,
        )


if __name__ == "__main__":
    main()
