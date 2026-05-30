import React from "react";
import Converter from "../components/Converter";
import HistoryWidget from "../components/HistoryWidget";

const ToolsPage: React.FC = () => (
  <div className="tools-grid">
    <Converter />
    <HistoryWidget />
  </div>
);

export default ToolsPage;
