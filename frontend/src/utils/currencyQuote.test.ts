import {
  baseCurrencyFromPair,
  chartRate,
  chartYAxisLabel,
  formatNbrbQuote,
  formatPerUnitNote,
  nbrbOfficialRate,
} from "./currencyQuote";

describe("nbrbOfficialRate", () => {
  it("returns official scale for RUB (100 units)", () => {
    expect(nbrbOfficialRate(0.03872, "RUB")).toBeCloseTo(3.872, 4);
  });

  it("returns official scale for TRY (10 units)", () => {
    expect(nbrbOfficialRate(0.06012, "TRY")).toBeCloseTo(0.6012, 4);
  });
});

describe("formatNbrbQuote", () => {
  it("formats USD per 1 unit", () => {
    expect(formatNbrbQuote("USD", 2.7596)).toBe("1 USD = 2.7596 BYN");
  });

  it("formats RUB per 100 units", () => {
    expect(formatNbrbQuote("RUB", 0.03872)).toBe("100 RUB = 3.8720 BYN");
  });

  it("formats UAH per 100 units", () => {
    expect(formatNbrbQuote("UAH", 0.062194)).toBe("100 UAH = 6.2194 BYN");
  });
});

describe("chartRate and chartYAxisLabel", () => {
  it("uses NBRB scale on chart Y axis", () => {
    expect(chartRate(0.03872, "RUB")).toBeCloseTo(3.872, 4);
    expect(chartYAxisLabel("RUB")).toBe("BYN за 100 RUB");
    expect(chartYAxisLabel("USD")).toBe("BYN за 1 USD");
  });
});

describe("formatPerUnitNote", () => {
  it("returns null for scale-1 currencies", () => {
    expect(formatPerUnitNote("USD", 2.7596)).toBeNull();
  });

  it("shows per-unit note for scaled currencies", () => {
    expect(formatPerUnitNote("RUB", 0.03872)).toBe("1 RUB ≈ 0.038720 BYN");
  });
});

describe("baseCurrencyFromPair", () => {
  it("extracts base currency code", () => {
    expect(baseCurrencyFromPair("RUB_BYN")).toBe("RUB");
    expect(baseCurrencyFromPair("USD_BYN")).toBe("USD");
  });
});
