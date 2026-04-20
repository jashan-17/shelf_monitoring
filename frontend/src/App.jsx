import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AboutPage from "./pages/AboutPage";
import PredictPage from "./pages/PredictPage";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/predict" element={<PredictPage />} />
        <Route path="/" element={<Navigate to="/predict" replace />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
