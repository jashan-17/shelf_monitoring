import { useEffect, useMemo, useRef, useState } from "react";
import ErrorBlock from "../components/ErrorBlock";
import PageHeader from "../components/PageHeader";
import { savePredictionResult, uploadPrediction } from "../services/api";

function PredictPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [savingResult, setSavingResult] = useState(false);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraSupportMessage, setCameraSupportMessage] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [hasSavedResult, setHasSavedResult] = useState(false);
  const [error, setError] = useState("");
  const [cameraError, setCameraError] = useState("");
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const previewUrl = useMemo(() => {
    if (!selectedFile) {
      return "";
    }
    return URL.createObjectURL(selectedFile);
  }, [selectedFile]);

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      stopCamera();
    };
  }, [previewUrl]);

  useEffect(() => {
    const attachCameraStream = async () => {
      if (!cameraOpen || !streamRef.current || !videoRef.current) {
        return;
      }

      try {
        videoRef.current.srcObject = streamRef.current;
        await videoRef.current.play();
        setCameraReady(true);
        setCameraError("");
      } catch (err) {
        setCameraReady(false);
        setCameraError("Camera stream opened, but the preview could not start.");
      }
    };

    attachCameraStream();
  }, [cameraOpen]);

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setCameraOpen(false);
    setCameraReady(false);
  };

  const openCamera = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraSupportMessage(
        "Camera access is unavailable in this browser. Try the latest Chrome, Edge, or Safari on localhost.",
      );
      setCameraError("This browser does not support camera access.");
      return;
    }

    if (!window.isSecureContext && window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
      setCameraSupportMessage(
        "Camera access requires HTTPS in deployment. It works on localhost during development.",
      );
      setCameraError("Camera access is blocked because this page is not running in a secure context.");
      return;
    }

    setCameraError("");
    setCameraSupportMessage("");
    setError("");
    setSaveMessage("");
    stopCamera();

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      setCameraOpen(true);
    } catch (err) {
      setCameraReady(false);

      if (err?.name === "NotAllowedError") {
        setCameraError("Camera permission was denied. Allow access in the browser and try again.");
      } else if (err?.name === "NotFoundError") {
        setCameraError("No camera was found on this device.");
      } else if (err?.name === "NotReadableError") {
        setCameraError("The camera is already in use by another application.");
      } else if (err?.name === "OverconstrainedError") {
        setCameraError("The requested camera settings are not supported on this device.");
      } else {
        setCameraError("Unable to access the device camera. Please check permissions and browser support.");
      }

      setCameraSupportMessage(
        "Camera access works on localhost in development. In production deployment, serve the app over HTTPS.",
      );
    }
  };

  const capturePhoto = async () => {
    if (!videoRef.current || !cameraReady) {
      setCameraError("Camera preview is not ready yet. Wait a moment and try again.");
      return;
    }

    const video = videoRef.current;
    if (video.readyState < 2 || !video.videoWidth || !video.videoHeight) {
      setCameraError("The camera frame is not available yet. Please wait for the preview to load.");
      return;
    }

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");

    if (!context) {
      setCameraError("Unable to capture photo from the camera feed.");
      return;
    }

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const file = await new Promise((resolve) => {
      canvas.toBlob((blob) => {
        if (!blob) {
          resolve(null);
          return;
        }
        resolve(new File([blob], `camera-capture-${Date.now()}.jpg`, { type: "image/jpeg" }));
      }, "image/jpeg", 0.92);
    });

    if (!file) {
      setCameraError("Failed to turn the camera capture into an image file.");
      return;
    }

    setSelectedFile(file);
    setResult(null);
    setHasSavedResult(false);
    setSaveMessage("");
    setError("");
    setCameraError("");
    stopCamera();
  };

  const handleFileChange = (event) => {
    const file = event.target.files?.[0];
    setSelectedFile(file || null);
    setResult(null);
    setHasSavedResult(false);
    setSaveMessage("");
    setError("");
    setCameraError("");
    setCameraSupportMessage("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError("Please choose an image before running a prediction.");
      return;
    }

    setLoadingPrediction(true);
    setError("");
    setSaveMessage("");
    try {
      const prediction = await uploadPrediction(selectedFile);
      setResult(prediction);
      setHasSavedResult(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingPrediction(false);
    }
  };

  const handleSaveResult = async () => {
    if (!result) {
      return;
    }

    setSavingResult(true);
    setError("");
    setSaveMessage("");
    try {
      await savePredictionResult({
        image_name: result.image_name || selectedFile?.name || "uploaded-image",
        predicted_label: result.predicted_label,
        confidence: result.confidence,
      });
      setHasSavedResult(true);
      setResult((currentResult) => ({
        ...currentResult,
        saved_to_database: true,
      }));
      setSaveMessage("Prediction saved to PostgreSQL.");
    } catch (err) {
      setError(err.message);
    } finally {
      setSavingResult(false);
    }
  };

  return (
    <section className="page-section">
      <PageHeader
        eyebrow="Live Prediction"
        title="Capture or upload a shelf image"
        description="This is now the main workflow: choose a shelf image from the device, or use the camera, run inference, and save the result only when you want it stored."
      />

      <div className="warning-note">
        <strong>Best results</strong>
        <p>
          Use clear shelf-focused images where the products fill most of the frame.
          Predictions may vary when the image includes large floor space, empty aisle
          area, strong glare, heavy blur, watermarks, or shelves captured from very far away.
        </p>
        <p>
          For the most reliable output, keep the shelf centered, well lit, and visible
          across the image before running prediction.
        </p>
      </div>

      <div className="predict-layout">
        <form className="card upload-card" onSubmit={handleSubmit}>
          <div className="capture-options">
            <label className="upload-dropzone">
              <span className="upload-title">Upload from device</span>
              <span className="upload-subtitle">
                Choose a shelf image from local storage.
              </span>
              <input type="file" accept="image/*" onChange={handleFileChange} />
            </label>

            <div className="camera-panel">
              <div className="camera-panel-header">
                <div>
                  <h3>Use device camera</h3>
                  <p className="card-copy">
                    Open the camera, capture a shelf image, and classify it immediately.
                  </p>
                </div>
                <button
                  className="button button-secondary"
                  type="button"
                  onClick={cameraOpen ? stopCamera : openCamera}
                >
                  {cameraOpen ? "Close camera" : "Open camera"}
                </button>
              </div>

              {cameraOpen ? (
                <div className="camera-preview-shell">
                  <video
                    ref={videoRef}
                    className="camera-preview"
                    autoPlay
                    playsInline
                    muted
                  />
                  <button
                    className="button"
                    type="button"
                    onClick={capturePhoto}
                    disabled={!cameraReady}
                  >
                    Capture photo
                  </button>
                </div>
              ) : (
                <div className="camera-placeholder">
                  Camera preview will appear here after you allow access.
                </div>
              )}

              {cameraError ? (
                <p className="inline-error">{cameraError}</p>
              ) : null}
              {cameraSupportMessage ? (
                <p className="card-copy">{cameraSupportMessage}</p>
              ) : null}
            </div>
          </div>

          {selectedFile ? (
            <div className="selected-file">
              <span>Selected image</span>
              <strong>{selectedFile.name}</strong>
            </div>
          ) : null}

          <button className="button" type="submit" disabled={loadingPrediction}>
            {loadingPrediction ? "Running prediction..." : "Run live prediction"}
          </button>

          {error ? <ErrorBlock message={error} /> : null}
        </form>

        <div className="card prediction-card">
          <div className="prediction-card-header">
            <div>
              <h3>Prediction result</h3>
              <p className="card-copy">
                Preview the chosen image and review the predicted shelf stock level.
              </p>
            </div>
            {result ? (
              <button
                className="button button-secondary"
                type="button"
                onClick={handleSaveResult}
                disabled={savingResult || hasSavedResult}
              >
                {hasSavedResult ? "Saved" : savingResult ? "Saving..." : "Save Result"}
              </button>
            ) : null}
          </div>

          {previewUrl ? (
            <img className="preview-image" src={previewUrl} alt="Shelf preview" />
          ) : (
            <div className="preview-placeholder">
              The selected or captured image preview will appear here.
            </div>
          )}

          {result ? (
            <div className="prediction-result">
              <div className="result-row">
                <span>Predicted label</span>
                <strong className={`tag tag-${result.predicted_label}`}>
                  {result.predicted_label}
                </strong>
              </div>
              <div className="result-row">
                <span>Confidence</span>
                <strong>{(result.confidence * 100).toFixed(1)}%</strong>
              </div>
              <div className="result-row">
                <span>Stored in database</span>
                <strong>{result.saved_to_database ? "Yes" : "Not yet"}</strong>
              </div>

              <div className="probability-list">
                {Object.entries(result.probabilities).map(([label, value]) => (
                  <div className="probability-row" key={label}>
                    <span>{label}</span>
                    <div className="probability-bar">
                      <div
                        className="probability-bar-fill"
                        style={{ width: `${value * 100}%` }}
                      />
                    </div>
                    <strong>{(value * 100).toFixed(1)}%</strong>
                  </div>
                ))}
              </div>

              {saveMessage ? <p className="success-text">{saveMessage}</p> : null}
            </div>
          ) : (
            <p className="card-copy">
              Run a live prediction to see the predicted label and confidence here.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

export default PredictPage;
