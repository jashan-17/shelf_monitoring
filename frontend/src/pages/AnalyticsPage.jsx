import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import ErrorBlock from "../components/ErrorBlock";
import LoadingBlock from "../components/LoadingBlock";
import PageHeader from "../components/PageHeader";
import { getStockLevels, getTrends } from "../services/api";

function AnalyticsPage() {
  const [stockLevels, setStockLevels] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAnalytics = async () => {
    setLoading(true);
    setError("");
    try {
      const [stockData, trendData] = await Promise.all([
        getStockLevels(),
        getTrends(7),
      ]);
      setStockLevels(stockData);
      setTrends(trendData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  if (loading) {
    return <LoadingBlock title="Loading analytics and trend data..." />;
  }

  if (error) {
    return <ErrorBlock message={error} onRetry={loadAnalytics} />;
  }

  return (
    <section className="page-section">
      <PageHeader
        eyebrow="Analytics"
        title="Distribution and recent trend analysis"
        description="These charts use aggregated counts and recent prediction history coming from the API layer."
        actions={
          <button className="button button-secondary" onClick={loadAnalytics}>
            Refresh charts
          </button>
        }
      />

      <div className="chart-grid">
        <div className="card chart-card">
          <div className="section-heading">
            <h3>Stock level distribution</h3>
            <p className="card-copy">
              Total prediction counts for each stock class.
            </p>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={stockLevels}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="stock_level" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="total_images" fill="#1f6feb" radius={[10, 10, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card chart-card">
          <div className="section-heading">
            <h3>Recent prediction trends</h3>
            <p className="card-copy">
              Daily prediction counts split by stock level.
            </p>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="empty" stroke="#d9485f" strokeWidth={3} />
              <Line type="monotone" dataKey="low" stroke="#ff8b3d" strokeWidth={3} />
              <Line type="monotone" dataKey="medium" stroke="#0c8f8f" strokeWidth={3} />
              <Line type="monotone" dataKey="full" stroke="#f5b700" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}

export default AnalyticsPage;
