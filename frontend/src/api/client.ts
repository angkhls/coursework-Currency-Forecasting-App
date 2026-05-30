import axios from "axios";
import type {
  ChartData,
  ConvertResult,
  CurrencyCode,
  CurrencyPair,
  CurrencyRate,
  BankRatesTable,
  DashboardResponse,
  ForecastMethod,
  ForecastResult,
  GoldCalcResult,
  MacroPanel,
  NewsFeed,
  ModelMetrics,
  PeriodPreset,
} from "../types";

const http = axios.create({
  baseURL: "/api/v1",
  timeout: 120000,
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).join(", ")
          : error.message ?? "Неизвестная ошибка";
    return Promise.reject(new Error(message));
  }
);

export const currencyApi = {
  getDashboard: async (): Promise<DashboardResponse> => {
    const { data } = await http.get("/dashboard");
    return data;
  },

  getAllLatest: async () => {
    const { data } = await http.get("/rates/all/latest");
    return data;
  },

  getHistory: async (currency: CurrencyCode, days = 30): Promise<CurrencyRate[]> => {
    const { data } = await http.get(`/rates/${currency}/history`, { params: { days } });
    return data;
  },

  getRateOnDate: async (currency: CurrencyCode, targetDate: string): Promise<CurrencyRate> => {
    const { data } = await http.get(`/rates/${currency}/on/${targetDate}`);
    return data;
  },

  getChart: async (pair: CurrencyPair, period: PeriodPreset): Promise<ChartData> => {
    const { data } = await http.get(`/pairs/${pair}/chart`, { params: { period } });
    return data;
  },

  getMacroBelarus: async (): Promise<MacroPanel> => {
    const { data } = await http.get("/macro/belarus");
    return data;
  },

  getBankRates: async (): Promise<BankRatesTable> => {
    const { data } = await http.get("/banks/minsk");
    return data;
  },

  calcGold: async (amount: number, currency: string): Promise<GoldCalcResult> => {
    const { data } = await http.get("/tools/gold", { params: { amount, currency } });
    return data;
  },

  getMacro: async (pair: CurrencyPair): Promise<MacroPanel> => {
    const { data } = await http.get(`/pairs/${pair}/macro`);
    return data;
  },

  getForecast: async (pair: CurrencyPair, days: number): Promise<ForecastResult> => {
    const { data } = await http.get(`/pairs/${pair}/forecast`, {
      params: { days, method: "sarimax" },
    });
    return data;
  },

  getMetrics: async (pair: CurrencyPair): Promise<ModelMetrics> => {
    const { data } = await http.get(`/pairs/${pair}/metrics`, { params: { method: "sarimax" } });
    return data;
  },

  compareMetrics: async (pair: CurrencyPair): Promise<Record<string, ModelMetrics>> => {
    const { data } = await http.get(`/pairs/${pair}/metrics/compare`);
    return data;
  },

  convert: async (
    amount: number,
    from: CurrencyCode,
    to: CurrencyCode
  ): Promise<ConvertResult> => {
    const { data } = await http.get("/convert", { params: { amount, from, to } });
    return data;
  },

  syncRates: async (currency: CurrencyCode) => {
    const { data } = await http.post(`/rates/${currency}/sync`);
    return data;
  },

  getNews: async (): Promise<NewsFeed> => {
    const { data } = await http.get("/news");
    return data;
  },
};
