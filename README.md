# CurrencyForecastingApp

Веб-приложение для **мониторинга и прогнозирования валютных курсов** (курсовая работа).

**Стек:** Python, FastAPI, React, API [НБРБ](https://www.nbrb.by/apihelp), SARIMAX (statsmodels).

## Откуда берутся данные

Официальные курсы валют к белорусскому рублю (BYN) загружаются с **API Национального банка Республики Беларусь**:

- `https://api.nbrb.by/exrates/rates/{id}` — курс на дату
- `https://api.nbrb.by/exrates/rates/dynamics/{id}` — история за период

Поддерживаются: **USD, EUR, RUB, CNY** (к BYN).

Пары для графиков и прогноза:

| Пара | Как считается |
|------|----------------|
| **USD/BYN** | курс доллара из НБРБ |
| **EUR/BYN** | курс евро из НБРБ |
| **EUR/USD** | кросс-курс: EUR÷USD по дням |

Данные кэшируются в **SQLite** (по умолчанию) или PostgreSQL.

## Как строится прогноз

### SARIMAX

Статистическая модель временных рядов (Seasonal ARIMA). Обучается на **истории официальных курсов за ~1 год**, затем экстраполирует на 1–30 дней. Параметры: `order=(1,1,1)`, `seasonal_order=(1,1,1,5)` (недельная сезонность по рабочим дням НБРБ).

### SMA(20) и EMA(20)

Считаются в `forecasting/service/technical.py` по **рабочим дням** (без субботы/воскресенья).

| Индикатор | Формула |
|-----------|---------|
| **SMA(20)** | `rolling(window=20, min_periods=1).mean()` — на «Неделе» и «Месяце» линия видна на всём графике |
| **EMA(20)** | `ewm(span=20, adjust=False)` |

Уровни **поддержка / сопротивление** — min/max за последние 20 точек.

### Метрики MAPE / RMSE

Backtest: последние 30 дней откладываются как «будущее», модель обучается на остальном и прогнозирует эти 30 дней; сравнение с фактом даёт MAPE (%) и RMSE.

---

## Установка с нуля (Linux)

### 1. Системные пакеты

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm
```

Проверка: `python3 --version` (≥3.10), `node --version` (≥18; у вас 18.19 — подходит).

### 2. Backend

```bash
cd forecasting
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Запуск API:

```bash
cd forecasting
source venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Если команда `uvicorn` не найдена — используйте `python -m uvicorn` (пакет ставится в venv через `pip install -r requirements.txt`).

Документация: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Откройте: http://localhost:3000

---

## Переменные окружения (`forecasting/.env`)

```env
STORAGE=sqlite
SQLITE_PATH=./data/currency.db
```

Для PostgreSQL + Docker:

```bash
cd infra
docker compose up -d
# в .env: STORAGE=postgres, DATABASE_URL=postgresql://currency_user:currency_pass@localhost:5432/currencydb
```

---

## Основные возможности UI

- Интерактивные графики: неделя / месяц / год (на дашборде также «день»)
- SMA(20), EMA(20), уровни поддержки и сопротивления
- Дашборд с актуальными курсами и % изменения за неделю
- Конвертер валют по курсам НБРБ
- Прогноз **SARIMAX** для USD/BYN, EUR/BYN, EUR/USD
- Метрики MAPE/RMSE на holdout

---

## Структура проекта

```
CurrencyForecastingApp/
├── forecasting/          # FastAPI + ML
│   ├── api/routes.py
│   ├── service/          # SARIMAX, тех. анализ
│   ├── infrastructure/   # NBRB, SQLite/Postgres
│   └── main.py
├── frontend/             # React + Vite + Recharts
└── infra/docker-compose.yml
```

---

## Архитектура и паттерны проектирования

### Какой стиль?

Проект — **многослойная архитектура (Layered Architecture)** с элементами **гексагональной (Ports & Adapters)**.

Это **не** классический Clean Architecture и **не** луковая (Onion) в чистом виде: нет отдельного слоя use-case на каждую операцию и domain не полностью изолирован от Pydantic/FastAPI. Зато зависимости направлены **от внешних слоёв к внутренним**: HTTP и БД не «протекают» в формулы прогноза.

```
┌─────────────────────────────────────────────────────────────┐
│  frontend/          React UI (презентация)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP /api/v1
┌───────────────────────────▼─────────────────────────────────┐
│  api/               FastAPI routes — адаптер входа (HTTP)     │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│  service/           сценарии: курсы, прогноз, график, банки   │
└───────┬───────────────────────────────┬─────────────────────┘
        │                               │
┌───────▼────────┐              ┌─────────▼──────────────────────┐
│  domain/       │              │  infrastructure/               │
│  модели,       │◄─────────────│  НБРБ, SQLite/Postgres, парсинг│
│  контракты     │   implements │  банков (адаптеры)             │
└────────────────┘              └────────────────────────────────┘
```

| Слой | Папка | Роль |
|------|--------|------|
| Presentation | `api/`, `frontend/` | REST, UI |
| Application | `service/` | Оркестрация: sync, chart, forecast, convert |
| Domain | `domain/` | Сущности (Pydantic), порт `CurrencyRateRepository` |
| Infrastructure | `infrastructure/` | Реализации порта и внешние API |

**Сборка зависимостей** — в `forecasting/main.py` (lifespan): создаётся репозиторий, клиент НБРБ, `RateService`, подмена `Depends` для FastAPI.

### Паттерны — где используются

| Паттерн | Где | Зачем |
|---------|-----|--------|
| **Strategy (Стратегия)** | `service/forecaster.py` — `BaseForecast`, `SARIMAXForecaster` | Интерфейс `predict()` для смены алгоритма прогноза |
| **Repository (Репозиторий)** | `domain/repositories.py` — `CurrencyRateRepository`; `infrastructure/sqlite_repository.py`, `db_repository.py` | Скрыть SQLite/PostgreSQL за контрактом «сохранить/прочитать курсы» |
| **Dependency Injection** | FastAPI `Depends(get_rate_service)`; `app.dependency_overrides` в `main.py` | Подставить реальные сервисы в тестах и при старте |
| **Adapter (Адаптер)** | `infrastructure/nbrb_client.py`, `belarusbank_client.py`, `myfin_client.py` | Привести внешние HTTP API к внутренним моделям |
| **DTO / Entity** | `domain/models.py` — `CurrencyRate`, `ChartData`, `ForecastResult` | Контракт данных между слоями и OpenAPI |
| **Facade (Фасад)** | `service/rate_service.py` — `RateService` | Единая точка для dashboard, chart, forecast, convert |
| **Template Method (частично)** | `BaseForecast.predict()` — общий контракт, детали в подклассах | Общий способ вызова прогноза |

Комментарии в коде с пометкой «ПАТТЕРН» есть в `forecaster.py`, `domain/repositories.py`, `infrastructure/db_repository.py`.

### Frontend

Отдельное SPA: **компоненты** (`components/`), **страницы** (`pages/`), **API-клиент** (`api/client.ts`). Прокси Vite `/api` → `localhost:8000`. Это классическое разделение UI / transport, без DDD на клиенте.

---

## API (кратко)

| Метод | Путь |
|-------|------|
| GET | `/api/v1/dashboard` |
| GET | `/api/v1/pairs/{pair}/chart?period=month` |
| GET | `/api/v1/pairs/{pair}/forecast?days=7&method=sarimax` |
| GET | `/api/v1/pairs/{pair}/metrics/compare` |
| GET | `/api/v1/convert?amount=100&from=USD&to=EUR` |
| GET | `/api/v1/rates/USD/on/2024-06-01` |

`pair`: `USD_BYN`, `EUR_BYN`, `EUR_USD`
