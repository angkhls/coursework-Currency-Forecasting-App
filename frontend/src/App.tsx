import React from "react";
import { BrowserRouter, Navigate, Route, Routes, useParams, useSearchParams } from "react-router-dom";
import Layout from "./components/Layout";
import ConverterPage from "./pages/ConverterPage";
import HomePage from "./pages/HomePage";
import NewsPage from "./pages/NewsPage";
import PairPage from "./pages/PairPage";

const HomeEntry: React.FC = () => {
  const [searchParams] = useSearchParams();
  if (searchParams.get("tab") === "news") {
    return <Navigate to="/news" replace />;
  }
  return <HomePage />;
};

const App: React.FC = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomeEntry />} />
        <Route path="/news" element={<NewsPage />} />
        <Route path="/converter" element={<ConverterPage />} />
        <Route path="/pair/:pair" element={<PairPage />} />
      </Route>
      <Route path="/live" element={<Navigate to="/" replace />} />
      <Route path="/market" element={<Navigate to="/" replace />} />
      <Route path="/forecast" element={<Navigate to="/pair/USD_BYN" replace />} />
      <Route path="/forecast/:pair" element={<LegacyForecastRedirect />} />
      <Route path="/tools" element={<Navigate to="/converter" replace />} />
      <Route path="/history" element={<Navigate to="/converter" replace />} />
      <Route path="/macro" element={<Navigate to="/" replace />} />
    </Routes>
  </BrowserRouter>
);

const LegacyForecastRedirect: React.FC = () => {
  const { pair } = useParams<{ pair: string }>();
  return <Navigate to={`/pair/${pair ?? "USD_BYN"}`} replace />;
};

export default App;
