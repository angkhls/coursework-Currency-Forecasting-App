# Отчёт о выполнении тест-кейсов — задание 3.4

**Проект:** Currency Forecasting App  
**Основание:** [План тестирования](test-plan.md), [Тест-кейсы](test-cases.md) (`TC-01`…`TC-32`)  
**Дата прогона:** 2026-11-16  
**Тестовая среда:** Linux (Python 3.11.2, FastAPI, Uvicorn, SQLite `test_exec.db` с 120-дневной историей по 10 валютам, локальные HTTP-заглушки НБРБ/Finnhub/Беларусбанк/Myfin)  
**Исполнитель:** Автоматизированный прогон `tests/run_tc_suite.py` + визуальная фиксация доказательств в [`docs/test-evidence/`](test-evidence/)

## 1. Сводка и расчёт метрик (по разделу 6 плана тестирования)

| Метрика | Формула | Значение |
|---|---|---|
| Всего запланировано тест-кейсов | — | 32 |
| Выполнено (`Pass + Fail`) | `31 + 1` (первичный) / `32 + 0` (после фикса) | 32 |
| `Blocked` / `Not Run` | — | 0 / 0 |
| **Процент выполнения (`Execution rate`)** | `32 / 32 × 100%` | **100.00%** |
| **Процент успешного прохождения (`Pass rate`)** | `31 / 32 × 100%` (до фикса) / `32 / 32 × 100%` (после) | **96.88% → 100.00%** |
| **Покрытие требований (`Requirements coverage`)** | `18 / 18 × 100%` | **100.00%** |
| Устранение дефектов `High` | `2 / 2 × 100%` (`DEF-01`, `DEF-07`) | **100.00%** |
| Устранение дефектов `Medium` | `3 / 3 × 100%` (`DEF-02`, `DEF-03`, `DEF-05`) | **100.00%** |
| Устранение дефектов `Low` | `2 / 2 × 100%` (`DEF-04`, `DEF-06`) | **100.00%** |
| Устранение дефектов `Critical/Blocker` | `0 / 0` | `N/A (дефектов данной важности не найдено)` |

## 2. Протокол выполнения тест-кейсов (`TC-01`…`TC-32`)

| ID | Приоритет | Требования | Фактический результат | Статус | Доказательство |
|---|---|---|---|---|---|
| TC-01 | High | FR-01, FR-12, FR-18 | HTTP 200; в ответе `/api/v1/dashboard` возвращено 10 валют (`USD..TRY`) с датой и изменением | **Pass** | [`TC-01-dashboard.png`](test-evidence/TC-01-dashboard.png) |
| TC-02 | High | FR-01, FR-16 | При отсутствии курса `TRY` `/api/v1/dashboard` вернул HTTP 200 (9 валют), `/api/v1/rates/TRY/latest` — HTTP 404 | **Pass** | — |
| TC-03 | High | FR-03 | `GET /api/v1/rates/USD/history?days=30` вернул HTTP 200 и список котировок за период | **Pass** | — |
| TC-04 | High | FR-03, FR-15 | `GET /api/v1/rates/USD/history?days=0` отклонён с HTTP 422 (`greater_than_equal=1`) | **Pass** | — |
| TC-05 | High | FR-02, FR-15 | `GET /api/v1/rates/XYZ/history?days=30` отклонён с HTTP 422 | **Pass** | — |
| TC-06 | Medium | FR-03 | `GET /api/v1/rates/USD/on/{date}` вернул HTTP 200 и курс на запрошенную дату | **Pass** | — |
| TC-07 | Medium | FR-15 | `GET /api/v1/rates/USD/on/not-a-date` отклонён с HTTP 422 | **Pass** | — |
| TC-08 | High | FR-12, FR-13 | Первичный прогон: HTTP 502 (`DEF-01` `get_latest_date`). После исправления на `get_latest` — HTTP 200 | **Fail → Pass** | [`TC-08-sync-fail.png`](test-evidence/TC-08-sync-fail.png) |
| TC-09 | High | FR-12, FR-16 | При timeout НБРБ `POST /api/v1/rates/USD/sync` вернул HTTP 502 с безопасным описанием ошибки | **Pass** | — |
| TC-10 | High | FR-11 | `GET /api/v1/convert?amount=100&from=RUB&to=USD` вернул HTTP 200, корректный кросс-курс и сумму | **Pass** | [`TC-10-convert.png`](test-evidence/TC-10-convert.png) |
| TC-11 | Medium | FR-11 | `GET /api/v1/convert?amount=50&from=USD&to=USD` вернул HTTP 200, `result=50.0`, `rate=1.0` | **Pass** | — |
| TC-12 | High | FR-11, FR-15 | `GET /api/v1/convert?amount=0&from=USD&to=EUR` отклонён с HTTP 422 | **Pass** | — |
| TC-13 | High | FR-11, FR-15 | `GET /api/v1/convert?amount=100&from=USD&to=XYZ` отклонён с HTTP 422 | **Pass** | — |
| TC-14 | High | FR-02, UC-02 | Пара `USD_BYN` вернула HTTP 200 и данные графика для `USD_BYN` | **Pass** | — |
| TC-15 | Medium | FR-02, FR-15 | Невалидная пара `XYZ` отклонена с HTTP 422 | **Pass** | — |
| TC-16 | High | FR-04 | `GET /api/v1/pairs/USD_BYN/chart?period=month` вернул HTTP 200, хронологический ряд точек | **Pass** | [`TC-16-chart.png`](test-evidence/TC-16-chart.png) |
| TC-17 | Medium | FR-04, FR-15 | Некорректный `period=bad_period` отклонён с HTTP 422 | **Pass** | — |
| TC-18 | High | FR-05, FR-06 | `GET /api/v1/pairs/USD_BYN/forecast?days=7&method=sarimax` вернул HTTP 200 и 7 точек прогноза | **Pass** | [`TC-18-forecast.png`](test-evidence/TC-18-forecast.png) |
| TC-19 | High | FR-05, FR-15 | При истории < 30 точек прогноз отклонён с HTTP 400 (`Недостаточно данных для прогноза`) | **Pass** | — |
| TC-20 | High | FR-05, FR-16 | При исключении модели прогноз вернул HTTP 502 | **Pass** | — |
| TC-21 | Medium | FR-10 | `GET /api/v1/pairs/USD_BYN/metrics?method=sarimax&holdout_days=30` вернул HTTP 200, числовые `mape` и `rmse` | **Pass** | — |
| TC-22 | Medium | FR-10, FR-15 | `holdout_days=3` отклонён с HTTP 422 (`greater_than_equal=7`) | **Pass** | — |
| TC-23 | Medium | FR-07 | В точках графика присутствует непустое значение `sma_20` | **Pass** | [`TC-16-chart.png`](test-evidence/TC-16-chart.png) |
| TC-24 | Medium | FR-08 | В точках графика присутствует непустое значение `ema_20` | **Pass** | [`TC-16-chart.png`](test-evidence/TC-16-chart.png) |
| TC-25 | Medium | FR-09 | Уровни `support <= resistance` вычислены корректно по окну графика | **Pass** | [`TC-16-chart.png`](test-evidence/TC-16-chart.png) |
| TC-26 | Medium | FR-14 | `GET /api/v1/news` вернул HTTP 200 и список статей | **Pass** | [`TC-26-news.png`](test-evidence/TC-26-news.png) |
| TC-27 | High | FR-14, FR-16 | При сбое Finnhub `GET /api/v1/news` вернул HTTP 502 | **Pass** | — |
| TC-28 | Medium | FR-11 | `GET /api/v1/tools/gold?amount=10&currency=BYN` вернул HTTP 200 и расчёт `gold_grams > 0` | **Pass** | — |
| TC-29 | High | FR-11, FR-15 | `GET /api/v1/tools/gold?amount=0&currency=BYN` отклонён с HTTP 422 | **Pass** | — |
| TC-30 | Medium | FR-11, FR-15 | `GET /api/v1/tools/gold?amount=10&currency=XXX` отклонён с HTTP 400 | **Pass** | — |
| TC-31 | High | FR-17 | Локальный backend запущен, `/health` и `/docs` вернули HTTP 200 | **Pass** | [`TC-31-swagger-ui.png`](test-evidence/TC-31-swagger-ui.png) |
| TC-32 | High | FR-01..03, FR-05, FR-11 | Сквозной сценарий `dashboard -> chart -> forecast -> convert` выполнен успешно (все ответы HTTP 200) | **Pass** | — |
