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
FINNHUB_API_KEY=ваш_ключ   # новости на главной
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
- Лента новостей рынка (Finnhub, категория `general`)

---

## Структура проекта

```
CurrencyForecastingApp/
├── forecasting/              # Backend
│   ├── api/routes.py         # HTTP-адаптер (Presentation)
│   ├── service/              # Сценарии приложения (Application)
│   ├── domain/               # Модели и порты (Domain)
│   ├── infrastructure/       # БД и внешние API (Infrastructure)
│   ├── config.py
│   └── main.py               # Composition Root — сборка зависимостей
├── frontend/                 # React SPA (отдельное приложение)
│   ├── src/pages/
│   ├── src/components/
│   └── src/api/client.ts
└── infra/docker-compose.yml
```

---

## Архитектура приложения (подробно)

Этот раздел написан для курсовой/защиты: здесь зафиксирован **стиль архитектуры**, **доказательства по коду**, **паттерны GoF** и **практическая ценность** такого проектирования.

### 1. К какому стилю относится проект?

**Основа — многослойная архитектура (Layered Architecture, n-tier).**  
**Дополнение — идеи гексагональной архитектуры (Hexagonal / Ports & Adapters).**

| Критерий | Что видно в репозитории | Вывод |
|----------|-------------------------|--------|
| Физическое разделение по папкам | `api/`, `service/`, `domain/`, `infrastructure/` | Есть явные слои |
| Направление зависимостей | `service/rate_service.py` импортирует `domain.repositories`, но **не** импортирует `api` | Бизнес-логика не зависит от HTTP |
| Порт хранилища | `domain/repositories.py` — абстрактный `CurrencyRateRepository` | Domain задаёт контракт, infrastructure реализует |
| Composition Root | `main.py` — единственное место, где «склеиваются» SQLite/Postgres, NBRB, сервисы | Зависимости собираются снаружи домена |

**Это не «чистый» Clean Architecture и не луковая (Onion) архитектура в учебнике:**

- В `domain/models.py` используется **Pydantic** (удобно для OpenAPI, но domain слегка связан с инфраструктурой сериализации).
- Нет отдельного класса UseCase на каждый HTTP-запрос — сценарии сгруппированы в `RateService` и `BankRatesService` (паттерн **Facade**).
- `main.py` знает и о `infrastructure`, и о `service` — это нормально для Composition Root.

**Гексагональность проявляется так:** ядро (`domain` + `service`) объявляет, *что* ему нужно (репозиторий, модели), а адаптеры (`infrastructure/*`, `api/routes.py`) подключаются снаружи.

### 2. Схема слоёв и потока данных

```
  [ Браузер ]
       │
       ▼
┌──────────────────┐
│    frontend/     │  Presentation (UI): React, Recharts
│  pages, components│
└────────┬─────────┘
         │ HTTP JSON  /api/v1/*
         ▼
┌──────────────────┐
│    api/routes    │  Driving Adapter: FastAPI, валидация, HTTP-коды
└────────┬─────────┘
         │ Depends → RateService, BankRatesService, FinnhubClient
         ▼
┌──────────────────┐
│    service/      │  Application: оркестрация сценариев
│  RateService     │
└────────┬─────────┘
         │ использует domain.models, CurrencyRateRepository (ABC)
         ▼
┌──────────────────┐       ┌─────────────────────────┐
│    domain/       │◄──────│   infrastructure/       │
│  models, ports   │ impl  │  SQLite, Postgres, NBRB, │
└──────────────────┘       │  Finnhub, парсинг банков │
                           └─────────────────────────┘
```

**Пример сквозного запроса** `GET /api/v1/pairs/USD_BYN/forecast?days=7`:

1. `routes.py` — принимает параметры, вызывает `service.get_forecast(...)`, переводит исключения в 400/502.
2. `RateService.get_forecast` — загружает историю через `_repo`, вызывает `SARIMAXForecaster.predict`, считает MAPE.
3. `SqliteCurrencyRateRepository` — читает кэш; при необходимости `sync_rates` тянет данные через `NbrbApiClient`.
4. `NbrbApiClient` — HTTP к api.nbrb.by, ответ → `CurrencyRate`.
5. Ответ сериализуется в `ForecastResult` (Pydantic) → JSON → React `MainChart`.

Ни `forecaster.py`, ни `technical.py` **не знают** про FastAPI и SQL — это и есть практическая польза слоёв.

### 3. Доказательство инверсии зависимостей (DIP)

**Правило DIP:** модули верхнего уровня не должны зависеть от модулей нижнего уровня; оба зависят от абстракций.

**Доказательство 1 — тип в конструкторе сервиса** (`service/rate_service.py`):

```python
class RateService:
    def __init__(
        self,
        repository: CurrencyRateRepository,  # абстракция из domain
        nbrb_client: NbrbApiClient,
    ):
```

`RateService` принимает **интерфейс** `CurrencyRateRepository`, а не `SqliteCurrencyRateRepository`.

**Доказательство 2 — папка `domain/` не импортирует `infrastructure/`:**  
в `forecasting/domain/` нет строк `from infrastructure` (можно проверить: `grep -r infrastructure domain/` → пусто).

**Доказательство 3 — слой `service/` не импортирует `api/`:**  
маршруты не протекают в расчёт SMA или SARIMAX.

**Доказательство 4 — сборка в `main.py`:**

```python
repository = SqliteCurrencyRateRepository(SQLITE_PATH)  # или Postgres
service = RateService(repository=repository, nbrb_client=nbrb)
app.dependency_overrides[get_rate_service] = _get_service
```

Конкретная БД выбирается **один раз** при старте; `RateService` остаётся неизменным при смене SQLite → PostgreSQL (достаточно поменять `STORAGE` в `.env`).

### 4. Слои backend — ответственность и файлы

#### 4.1. Presentation — `api/routes.py`

- Только HTTP: маршруты, `Query`, `HTTPException`, `response_model`.
- Не содержит формул прогноза и SQL.
- **Доказательство:** метод `get_forecast` — 3 строки логики + обработка ошибок; вся математика в `RateService`.

#### 4.2. Application — `service/`

| Модуль | Ответственность |
|--------|-----------------|
| `rate_service.py` | Курсы, график, прогноз, конвертер, дашборд |
| `forecaster.py` | Алгоритм SARIMAX |
| `technical.py` | SMA, EMA, support/resistance |
| `bank_rates_service.py` | Сводная таблица банков Минска |
| `macro_service.py` | Макро-панель |
| `calendar_utils.py` | Рабочие дни НБРБ, разворот прогноза на календарь |
| `metrics_calc.py` | MAPE, RMSE |
| `pairs.py` | Логика пар USD_BYN, EUR_USD |

#### 4.3. Domain — `domain/`

- `models.py` — DTO/сущности: `CurrencyRate`, `ChartData`, `ForecastResult`, `NewsArticle`…
- `repositories.py` — **порт** персистентности `CurrencyRateRepository(ABC)`.

Domain отвечает на вопрос: *какие данные и какие операции существуют в предметной области*, без привязки к SQLite или httpx.

#### 4.4. Infrastructure — `infrastructure/`

| Адаптер | Внешняя система |
|---------|-----------------|
| `nbrb_client.py` | API НБРБ |
| `sqlite_repository.py` | SQLite |
| `db_repository.py` | PostgreSQL |
| `belarusbank_client.py`, `myfin_client.py` | Курсы банков |
| `finnhub_client.py` | Новости Finnhub |

### 5. Паттерны проектирования (GoF и архитектурные) — где, зачем, доказательство

#### 5.1. Repository (Репозиторий)

**Суть:** коллекция объектов домена, доступ к которой инкапсулирован так, будто это in-memory коллекция.

**Где:**  
- Порт: `domain/repositories.py` — `class CurrencyRateRepository(ABC)` с методами `save`, `get_history`, `get_latest`…  
- Реализации: `SqliteCurrencyRateRepository`, `PostgresCurrencyRateRepository`.

**Почему:**  
- `RateService` не пишет `SELECT * FROM currency_rates` — проще тестировать и менять БД.  
- В коде прямо указано: *«domain не зависит от БД»* (комментарий в `repositories.py`).

**Доказательство в runtime:** в `main.py` при `STORAGE=postgres` подставляется другой класс, интерфейс сервиса тот же.

---

#### 5.2. Strategy (Стратегия)

**Суть:** семейство алгоритмов, взаимозаменяемых через общий интерфейс.

**Где:** `service/forecaster.py`:

```python
class BaseForecast(ABC):
    @abstractmethod
    def predict(self, rates: List[CurrencyRate], days: int) -> List[ForecastPoint]:
        ...

class SARIMAXForecaster(BaseForecast):
    def predict(self, rates, days):
        ...
```

**Почему:** `RateService` вызывает `self._sarimax.predict(...)`; при добавлении нового алгоритма достаточно нового класса `BaseForecast`, без переписывания HTTP-слоя.

**Доказательство расширяемости:** в `get_forecast` и `_evaluate_holdout` прогноз идёт через один метод `predict` — контракт стратегии соблюдён.

---

#### 5.3. Adapter (Адаптер)

**Суть:** преобразует интерфейс класса в другой интерфейс, ожидаемый клиентом.

**Где:** `infrastructure/nbrb_client.py` — комментарий «ПАТТЕРН: Adapter»; JSON НБРБ → `CurrencyRate`.

**Почему:** формат НБРБ (числовые `Cur_ID`, поля `Cur_OfficialRate`) не должен расползаться по `service/`.

Аналогично: `FinnhubClient` → `NewsArticle`, парсеры HTML в `myfin_client.py`.

---

#### 5.4. Facade (Фасад)

**Суть:** упрощённый интерфейс к сложной подсистеме.

**Где:** `RateService` — один класс с методами `get_dashboard`, `get_chart`, `get_forecast`, `convert`, `sync_rates`.

**Почему:** `routes.py` не координирует вручную репозиторий + NBRB + SARIMAX + technical — он вызывает один фасад.

**Доказательство:** эндпоинт `/dashboard` — одна строка `return await service.get_dashboard()`.

---

#### 5.5. Dependency Injection (внедрение зависимостей)

**Суть:** зависимости передаются извне, а не создаются внутри класса.

**Где:**  
- FastAPI: `Depends(get_rate_service)` во всех маршрутах.  
- `main.py`: `app.dependency_overrides[get_rate_service] = _get_service`.

**Почему:**  
- Удобно подменить сервис в тестах (mock `CurrencyRateRepository`).  
- Единая точка конфигурации (Composition Root).

**Доказательство:** `get_rate_service()` в `routes.py` по умолчанию бросает `NotImplementedError` — без `main.py` приложение не «собрано»; это явный признак DI через композицию.

---

#### 5.6. DTO / Data Transfer Object

**Где:** `domain/models.py` — Pydantic-модели для API и внутреннего обмена.

**Почему:** единый контракт для OpenAPI (`response_model=ChartData`) и для frontend TypeScript-типов.

---

#### 5.7. Composition Root (корень композиции)

**Где:** `forecasting/main.py`, функция `lifespan`.

**Почему:** только здесь создаются «конкретики» (пул Postgres, путь SQLite, ключ Finnhub). Остальные модули получают готовые объекты.

Это архитектурный приём из DDD/Clean, даже если весь Clean не соблюдён формально.

---

### 6. В чём «прелесть» такой архитектуры для этого проекта?

1. **Изменения локализованы.** Новый источник курсов = новый файл в `infrastructure/`, без правок SARIMAX.  
2. **Тестируемость.** Можно подставить in-memory репозиторий и проверить `get_forecast` без NBRB и SQLite.  
3. **Читаемость для защиты.** Экзаменатор видит папки и сразу понимает: «вот HTTP, вот бизнес, вот БД».  
4. **Параллельная разработка.** Один разработчик делает UI, другой — `NbrbApiClient`, третий — прогноз; стык через `CurrencyRate` и OpenAPI.  
5. **Смена окружения.** SQLite для курсовой, Postgres в Docker — переключатель в `config.py`, не рефакторинг сервиса.  
6. **Прогноз и график изолированы.** `technical.py` и `forecaster.py` — чистая математика/pandas, их можно описать в пояснительной записке отдельно от React.

### 7. Архитектура frontend (кратко, для полноты картины)

Frontend — **отдельное SPA**, не «слой» backend в смысле DDD:

| Часть | Роль |
|-------|------|
| `pages/` | Экраны: `HomePage`, `PairPage`, `ConverterPage` |
| `components/` | Переиспользуемые блоки: `MainChart`, `NewsPanel`, `Converter` |
| `api/client.ts` | Единый HTTP-клиент (axios), обработка ошибок API |
| `types/` | Зеркало Pydantic-моделей backend |

Связь с backend — **только HTTP** (`vite.config.ts` проксирует `/api` → `:8000`). Это **клиент–серверная** архитектура: два приложения, один контракт REST.

Новости — отдельная страница `/news`, пункт в боковой панели.

### 8. Сравнительная таблица (для пояснительной записки)

| Подход | Есть в проекте? | Комментарий |
|--------|----------------|-------------|
| Монолит без слоёв | ❌ | Код разделён по папкам и ролям |
| Layered (n-tier) | ✅ | `api` → `service` → `domain` / `infrastructure` |
| Hexagonal | ✅ частично | Порты (`CurrencyRateRepository`), адаптеры (NBRB, Finnhub) |
| Clean Architecture | ⚠️ частично | DIP и Composition Root есть; Pydantic в domain |
| Onion | ⚠️ частично | Domain в центре по зависимостям, но без строгих колец |
| Микросервисы | ❌ | Один backend + один frontend |

### 9. Где смотреть в коде при защите (чеклист)

1. **Слои:** дерево `forecasting/` — 4 папки.  
2. **Repository:** `domain/repositories.py` + `sqlite_repository.py`.  
3. **Strategy:** `forecaster.py`, класс `BaseForecast`.  
4. **Adapter:** `nbrb_client.py`, строки про NBRB → `CurrencyRate`.  
5. **DI:** `routes.py` `Depends`, `main.py` `dependency_overrides`.  
6. **Facade:** `rate_service.py`, метод `get_chart`.  
7. **Composition Root:** `main.py`, `lifespan`.  
8. **Сквозной сценарий:** открыть Swagger `/docs` → `GET /pairs/USD_BYN/chart` → проследить вызов в `RateService.get_chart`.

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
| GET | `/api/v1/news` |

`pair`: `USD_BYN`, `EUR_BYN`, `EUR_USD`
