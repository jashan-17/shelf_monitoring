import { useEffect, useState } from "react";
import DataTable from "../components/DataTable";
import ErrorBlock from "../components/ErrorBlock";
import LoadingBlock from "../components/LoadingBlock";
import PageHeader from "../components/PageHeader";
import StatCard from "../components/StatCard";
import StatusCard from "../components/StatusCard";
import { getPredictions, getSummary, getSystemStatus } from "../services/api";

function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const [summaryData, predictionData, statusData] = await Promise.all([
        getSummary(),
        getPredictions(10),
        getSystemStatus(),
      ]);
      setSummary(summaryData);
      setPredictions(predictionData);
      setSystemStatus(statusData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  if (loading) {
    return <LoadingBlock title="Loading dashboard metrics and recent predictions..." />;
  }

  if (error) {
    return <ErrorBlock message={error} onRetry={loadDashboard} />;
  }

  return (
    <section className="page-section">
      <PageHeader
        eyebrow="Dashboard"
        title="Shelf stock overview"
        description="A quick operational view of predictions coming from your existing model and PostgreSQL pipeline."
        actions={
          <button className="button button-secondary" onClick={loadDashboard}>
            Refresh
          </button>
        }
      />

      <div className="card-grid four-up">
        <StatCard
          label="Total Predictions"
          value={summary.total_predictions}
          accent="blue"
          hint="All records currently stored in PostgreSQL."
        />
        <StatCard
          label="Average Confidence"
          value={`${(summary.average_confidence * 100).toFixed(1)}%`}
          accent="green"
          hint="Mean confidence across all prediction records."
        />
        <StatCard
          label="Empty Shelves"
          value={summary.counts_by_class.empty}
          accent="red"
          hint="Detected images with empty stock level."
        />
        <StatCard
          label="Full Shelves"
          value={summary.counts_by_class.full}
          accent="gold"
          hint="Detected images with full stock level."
        />
      </div>

      <div className="card-grid four-up">
        <StatCard
          label="Low Stock"
          value={summary.counts_by_class.low}
          accent="orange"
        />
        <StatCard
          label="Medium Stock"
          value={summary.counts_by_class.medium}
          accent="teal"
        />
      </div>

      {systemStatus ? (
        <div className="card-grid three-up">
          <StatusCard {...systemStatus.database} />
          <StatusCard {...systemStatus.airflow} />
          <StatusCard
            label={systemStatus.dbt.label}
            status={systemStatus.dbt.status}
            detail={systemStatus.dbt.detail}
          />
        </div>
      ) : null}

      <div>
        <div className="section-heading">
          <h3>Latest prediction records</h3>
          <p className="card-copy">
            Recent rows from the `raw_predictions` table.
          </p>
        </div>
        <DataTable rows={predictions} />
      </div>
    </section>
  );
}

export default DashboardPage;
