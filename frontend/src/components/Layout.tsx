import React from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import { PAIR_LABELS } from "../types";
import type { CurrencyPair } from "../types";

const Layout: React.FC = () => {
  const { pathname } = useLocation();

  let title = "Главная";
  let subtitle = "О приложении, мониторинг и банки";

  if (pathname === "/converter") {
    title = "Конвертер";
    subtitle = "Перевод валют и расчёт золота";
  } else if (pathname.startsWith("/pair/")) {
    const pair = pathname.replace("/pair/", "") as CurrencyPair;
    title = PAIR_LABELS[pair] ?? "Валютная пара";
    subtitle = "График, выбор модели, MAPE / RMSE";
  }

  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <header className="topbar">
          <div>
            <h1>{title}</h1>
            <p className="topbar__greeting">Welcome back, Anhelina! {subtitle}</p>
          </div>
          <div className="topbar__user">
            <span>Anhelina</span>
            <div className="avatar">A</div>
          </div>
        </header>
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
