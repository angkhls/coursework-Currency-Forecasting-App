import React from "react";
import Converter from "../components/Converter";
import HistoryWidget from "../components/HistoryWidget";

const ConverterPage: React.FC = () => (
  <div className="converter-page">
    <div className="tools-grid">
      <Converter />
      <HistoryWidget />
    </div>
  </div>
);

export default ConverterPage;
