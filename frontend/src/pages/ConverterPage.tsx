import React from "react";
import Converter from "../components/Converter";
import GoldCalculator from "../components/GoldCalculator";
import HistoryWidget from "../components/HistoryWidget";

const ConverterPage: React.FC = () => (
  <div className="converter-page">
    <div className="tools-grid">
      <Converter />
      <GoldCalculator />
    </div>
    <div style={{ maxWidth: 420, margin: "0 2rem 2rem" }}>
      <HistoryWidget />
    </div>
  </div>
);

export default ConverterPage;
