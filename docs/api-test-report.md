# Отчёт о тестировании API (Postman-коллекция) — задание 4.2

Коллекция: tests/postman/CurrencyForecastingApp.postman_collection.json
Базовый адрес: 127.0.0.1:8000
Дата прогона: 2026-11-16

## 1. Связывание запросов и покрытие
- Позитивные проверки: статус 200, структура JSON, типы и значения полей.
- Негативные проверки: XYZ -> 422, amount=0 -> 422, несуществующий маршрут -> 404.
- Связывание запросов (Chaining): из 02. Dashboard извлекаются selectedCurrency, selectedPair и latestDate для запросов 03, 04, 05, 07, 08, 09, 10.

## 2. Результаты прогона
Итого: 15/16 PASS до исправления DEF-07 (06. All Latest Rates возвращал 422), 16/16 PASS после исправления 4c40acd.
- 01. GET /health -> 200 PASS (1.9 ms)
- 02. GET /api/v1/dashboard -> 200 PASS (4.8 ms)
- 03. GET /api/v1/rates/USD/latest -> 200 PASS (1.7 ms)
- 04. GET /api/v1/rates/USD/history?days=30 -> 200 PASS (2.1 ms)
- 05. GET /api/v1/rates/USD/on/{latestDate} -> 200 PASS (1.4 ms)
- 06. GET /api/v1/rates/all/latest -> 422 (DEF-07) -> 200 PASS (1.5 ms)
- 07. GET /api/v1/pairs/USD_BYN/chart?period=month -> 200 PASS (4.3 ms)
- 08. GET /api/v1/pairs/USD_BYN/forecast?days=7&method=sarimax -> 200 PASS (18.2 ms)
- 09. GET /api/v1/pairs/USD_BYN/metrics?method=sarimax&holdout_days=30 -> 200 PASS (9.5 ms)
- 10. GET /api/v1/convert?amount=100&from=USD&to=EUR -> 200 PASS (2.3 ms)
- 11. GET /api/v1/tools/gold?amount=500&currency=BYN -> 200 PASS (1.1 ms)
- 12. GET /api/v1/macro/belarus -> 200 PASS (1.0 ms)
- 13. GET /api/v1/news -> 200 PASS (1.2 ms)
- 14. GET /api/v1/rates/XYZ/history?days=30 -> 422 PASS (1.1 ms)
- 15. GET /api/v1/convert?amount=0&from=USD&to=EUR -> 422 PASS (1.0 ms)
- 16. GET /api/v1/unknown/endpoint -> 404 PASS (0.8 ms)
