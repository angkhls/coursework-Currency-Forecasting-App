# Отчёт о статической проверке кода (линтер) — задание 5.4

Объект проверки: Backend forecasting/ и Frontend .eslintrc.cjs.

## 1. Выявленные нарушения (до исправления — 10 нарушений в Python)
- forecasting/api/routes.py:2 — F401 неиспользуемые импорты Dict, Optional (исправлено в 4c40acd).
- forecasting/infrastructure/belarusbank_client.py:4 — F401 неиспользуемый импорт BankRatesTable.
- forecasting/service/macro_service.py:2-3 — F401 неиспользуемые импорты ET, date; избыточное условие unit = "USD" if id_key != "btc" else "USD".
- forecasting/service/pairs.py:1 — F401 неиспользуемый импорт PAIR_LABELS.
- forecasting/main.py:97, bank_rates_service.py:24/32, macro_service.py:82 — B110 подавление исключений except Exception: pass без логирования.

## 2. Результат после исправлений
Повторная проверка: Static issues after fix: 0.
