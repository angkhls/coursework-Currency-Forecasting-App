# Карта выполнения заданий

Этот файл — оглавление материалов по заданиям 1–5 проекта **Currency Forecasting App**. Ссылки ведут к спецификациям, тестам, отчётам о выполнении, доказательствам и исправлениям.

## Задание 1 — описание проекта, требования и верификация

- **1.1 Описание проекта:** [README.md](../README.md), разделы 1–6 (запуск backend: `uvicorn main:app --port 8000`, frontend: `npm run dev`).
- **1.2 Спецификация требований:** [docs/requirements.md](requirements.md) (`BR-01…BR-04`, `UC-01…UC-07`, `FR-01…FR-18`, `NFR-01…NFR-06`).
- **1.3 Верификация требований и дефекты:** [docs/verification.md](verification.md), [ISSUES.md](../ISSUES.md).
- **1.4 Диаграмма состояний:** [docs/state-diagram.md](state-diagram.md).

## Задание 2 — тесты и покрытие кода

- **2.1 Модульные, интеграционные и сценарные тесты:** [`forecasting/tests/`](../forecasting/tests/) (`python -m pytest -q`).
- **2.2 Покрытие кода ≥ 70%:** `pytest --cov=api --cov=service --cov=domain --cov=infrastructure --cov=main --cov-fail-under=70`.

## Задание 3 — планирование и выполнение тестирования

- **3.1 План тестирования:** [docs/test-plan.md](test-plan.md) (цель, области/исключения со ссылками на FR/NFR, стратегия, критерии начала/приостановки/возобновления/завершения, формулы метрик).
- **3.2 Чек-лист функциональных требований:** [docs/test-checklist.md](test-checklist.md) (позитивные и негативные проверки для `FR-01…FR-18`, выполнено `18 / 18`).
- **3.3 Тест-кейсы:** [docs/test-cases.md](test-cases.md) (32 тест-кейса `TC-01…TC-32`, 100% покрытие High FR).
- **3.4 Выполнение тест-кейсов и доказательства:** [docs/test-execution.md](test-execution.md) и скриншоты в [`docs/test-evidence/`](test-evidence/) (`Execution rate = 100%`, первичный `Pass rate = 96.88%`, после исправления `DEF-01` — `100%`).
- **3.5 Описание найденных дефектов:** [docs/test-defects.md](test-defects.md) (зафиксированы `DEF-01…DEF-07` со всеми обязательными атрибутами).

## Задание 4 — UI, API (Postman), безопасность и автоматизация UI

- **4.1 Тестирование вёрстки и совместимости:** [docs/ui-compatibility-report.md](ui-compatibility-report.md) (проверка сетки, адаптивности, интерактивных элементов, `favicon.svg`, таблица совместимости по браузерам и мобильной эмуляции).
- **4.2 Тестирование API в Postman:**
  - Коллекция: [`tests/postman/CurrencyForecastingApp.postman_collection.json`](../tests/postman/CurrencyForecastingApp.postman_collection.json) (позитивные, негативные, связывание переменных из `/dashboard`).
  - Скрипт прогона и отчёт: [`tests/postman/run_postman_collection.py`](../tests/postman/run_postman_collection.py), [docs/api-test-report.md](api-test-report.md) (`15/16` до фикса `DEF-07`, `16/16 PASS` после фикса).
- **4.3 Базовые проверки безопасности:** [docs/security-check.md](security-check.md) (проверка доступа без авторизации, IDOR, утечки ошибок `DEF-02`, логирования).
- **4.4 UI-автотесты (Selenium Page Object):** [`tests/ui_selenium/test_ui_e2e.py`](../tests/ui_selenium/test_ui_e2e.py) (`pages/base_page.py`, `home_page.py`, `converter_page.py`, `pair_page.py` — явные ожидания `WebDriverWait`, изолированные данные, сохранение скриншота при падении).

## Задание 5 — нагрузочное тестирование, линтер и трассируемость

- **5.1–5.3 План, прогоны и результаты нагрузочного тестирования:** [docs/load-testing-report.md](load-testing-report.md), [`tests/load/locustfile.py`](../tests/load/locustfile.py), [`tests/load/run_load_test.py`](../tests/load/run_load_test.py), график [`docs/test-evidence/load-test-chart.png`](test-evidence/load-test-chart.png) (точка деградации — 50 пользователей, анализ узких мест).
- **5.4 Статическая проверка кода (линтер) и исправления:** [docs/linting-report.md](linting-report.md) (выявлено и исправлено 10 нарушений в `forecasting/`, итоговый прогон — `0` нарушений).
- **5.5 Матрица трассируемости:** [docs/traceability-matrix.md](traceability-matrix.md) (`100%` покрытие `FR-01…FR-18`, 0 требований без тестов, выделены зоны высокого риска).

## Перед сдачей

- [x] Проверить, что все ссылки открываются.
- [x] Провести актуальный запуск backend-приложения (`/health`, `/docs`, `/api/v1/*`).
- [x] Для задания 3 заполнить отчёт фактического выполнения всех кейсов, приложить скриншоты и описать обнаруженные дефекты (`DEF-01…DEF-07`).
- [x] Для задания 4 подготовить отчёты по вёрстке/совместимости, Postman-коллекцию с отчётом, аудит безопасности и Selenium Page Object автотесты.
- [x] Для задания 5 провести нагрузочное и стресс-тестирование с графиком, статический анализ с исправлениями и построить матрицу трассируемости.
