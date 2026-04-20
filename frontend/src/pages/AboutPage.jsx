import PageHeader from "../components/PageHeader";

const features = [
  "Upload or capture a shelf image",
  "Predict stock level: empty, low, medium, or full",
  "Show confidence score",
  "Save results to PostgreSQL",
];

const workflowNotes = [
  "Frontend captures the image",
  "Backend runs the TFLite model",
  "Prediction returns instantly",
  "Result can be saved to the database",
];

const imageGuidance = [
  "Use clear shelf-focused images",
  "Keep products visible across most of the frame",
  "Avoid large floor or aisle areas when possible",
  "Predictions may vary on low-quality or heavily watermarked images",
];

const techStack = [
  "React (Frontend)",
  "FastAPI (Backend)",
  "TensorFlow Lite (Model Runtime)",
  "PostgreSQL (Database)",
];

function AboutPage() {
  return (
    <section className="page-section">
      <PageHeader
        eyebrow="About"
        title="Shelf Monitoring System"
        description="Image-based stock level classification for retail shelf monitoring with live prediction and optional database save."
      />

      <div className="about-hero card">
        <div className="about-hero-copy">
          <span className="about-kicker">Product Overview</span>
          <h3>Track shelf stock from images in a simple workflow</h3>
          <p className="card-copy">
            This application classifies supermarket shelf images into stock levels,
            returns confidence scores in real time, and lets users save selected
            results to PostgreSQL when they want them recorded.
          </p>
        </div>
        <div className="about-highlight-grid">
          {features.map((item) => (
            <div className="about-mini-card" key={item}>
              <strong>{item}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="about-section-grid">
        <div className="card about-content-card">
          <span className="eyebrow">What It Does</span>
          <h3>Core workflow</h3>
          <div className="about-list">
            {features.map((item) => (
              <div className="about-list-item" key={item}>
                <span className="about-list-marker" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card about-content-card">
          <span className="eyebrow">Why It Matters</span>
          <h3>Retail shelf visibility</h3>
          <p className="card-copy">
            Manual shelf monitoring is slow and inconsistent. This system
            supports more scalable image-based stock tracking.
          </p>
        </div>
      </div>

      <div className="about-section-grid">
        <div className="card about-content-card">
          <span className="eyebrow">Image Guidance</span>
          <h3>What works best</h3>
          <div className="about-list">
            {imageGuidance.map((item) => (
              <div className="about-list-item" key={item}>
                <span className="about-list-marker" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card about-content-card">
          <span className="eyebrow">Current State</span>
          <h3>Ready for demo and iteration</h3>
          <p className="card-copy">
            The app is ready for local demo use with upload, camera capture,
            prediction, and database save. Model performance is strongest on
            clear shelf images and can be improved further with more
            production-style training data.
          </p>
        </div>
      </div>

      <div className="card about-workflow-card">
        <div className="section-heading">
          <h3>How It Works</h3>
          <p className="card-copy">Image → Model → Prediction → Database</p>
        </div>
        <div className="about-flow-grid">
          {workflowNotes.map((item) => (
            <div className="about-flow-step" key={item}>
              <strong>{item}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="card about-content-card">
        <span className="eyebrow">Tech Stack</span>
        <h3>Built with</h3>
        <div className="about-list">
          {techStack.map((item) => (
            <div className="about-list-item" key={item}>
              <span className="about-list-marker" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default AboutPage;
