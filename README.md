# Currency Forecasting App

## 1. Название, назначение, целевые пользователи

Currency Forecasting App — веб-приложение для мониторинга и прогнозирования курсов валют. Проект собирает официальные курсы НБРБ, отображает динамику изменения валют по периодам, рассчитывает краткосрочные прогнозы и показывает технические индикаторы (SMA/EMA, уровни поддержки и сопротивления).

Основная задача приложения — дать пользователю быстрый и удобный доступ к данным по валютным курсам и прогнозной аналитике для принятия решений о покупке, продаже или сравнении курсов.

Целевые пользователи:
- частные лица, совершающие операции с валютой;
- туристы и путешественники;
- сотрудники компаний, работающих с зарубежными контрактами;
- аналитики и студенты, изучающие финансовые рынки;
- пользователи, интересующиеся прогнозированием курсов на основе статистических моделей.

## 2. Стек технологий

- Язык программирования: Python, TypeScript
- Backend: FastAPI, Uvicorn
- Frontend: React + Vite + TypeScript
- UI и визуализация: Recharts, CSS
- Аналитика: pandas, numpy, statsmodels (SARIMAX)
- СУБД: SQLite по умолчанию, PostgreSQL в Docker/инфраструктурном окружении
- Внешние источники данных: API НБРБ, Finnhub, парсинг данных банковских ресурсов
- Тестирование: pytest, Vitest
- Контейнеризация: Docker Compose

## 3. Архитектура системы

```mermaid
flowchart LR
    U[Пользователь] --> FE[Frontend / React SPA]
    FE --> API[FastAPI API / forecasting/api/routes.py]
    API --> SRV[Service layer / forecasting/service]
    SRV --> DOMAIN[Domain models / forecasting/domain]
    SRV --> REPO[(SQLite / PostgreSQL)]
    SRV --> NBRB[NBRB API]
    SRV --> BANK[Bank parsers]
    SRV --> FINNHUB[Finnhub API]
    FE --> CHART[Recharts / графики]
    FE --> CONV[Конвертер валют]
    FE --> NEWS[Лента новостей]
