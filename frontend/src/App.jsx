import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AnalyticsPage from "./pages/AnalyticsPage";
import AboutPage from "./pages/AboutPage";
import DashboardPage from "./pages/DashboardPage";
import PredictPage from "./pages/PredictPage";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/predict" element={<PredictPage />} />
        <Route path="/" element={<Navigate to="/predict" replace />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
