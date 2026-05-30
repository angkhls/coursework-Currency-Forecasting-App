from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from domain.models import CurrencyRate, CurrencyCode

# ─────────────────────────────────────────────
# ПАТТЕРН: Repository (Репозиторий)
#
# Абстрактный класс (ABC) описывает ИНТЕРФЕЙС —
# то есть ЧТО можно делать с данными, но НЕ КАК.
#
# Конкретные реализации (PostgreSQL, in-memory и т.д.)
# будут в папке infrastructure/.
#
# Это даёт нам:
# - Инверсию зависимостей (domain не зависит от БД)
# - Лёгкую замену хранилища без изменения бизнес-логики
# - Возможность тестирования с mock-репозиторием
# ─────────────────────────────────────────────

class CurrencyRateRepository(ABC):
    """
    Абстрактный репозиторий курсов валют.
    Определяет контракт для любого хранилища курсов.
    """

    @abstractmethod
    async def save(self, rate: CurrencyRate) -> None:
        """
        Сохранить один курс валюты.
        Если запись на эту дату уже есть — обновить.
        """
        ...

    @abstractmethod
    async def save_many(self, rates: List[CurrencyRate]) -> None:
        """
        Сохранить список курсов за раз (bulk insert).
        Эффективнее чем вызывать save() в цикле.
        """
        ...

    @abstractmethod
    async def get_by_currency_and_date(
        self,
        currency: CurrencyCode,
        target_date: date
    ) -> Optional[CurrencyRate]:
        """
        Получить курс конкретной валюты на конкретную дату.
        Возвращает None если запись не найдена.
        """
        ...

    @abstractmethod
    async def get_history(
        self,
        currency: CurrencyCode,
        from_date: date,
        to_date: date
    ) -> List[CurrencyRate]:
        """
        Получить историю курсов валюты за период.
        Используется для построения прогноза и графиков.
        Результат отсортирован по дате по возрастанию.
        """
        ...

    @abstractmethod
    async def get_latest(
        self,
        currency: CurrencyCode
    ) -> Optional[CurrencyRate]:
        """
        Получить самый свежий курс валюты.
        Используется для проверки актуальности данных.
        """
        ...

    @abstractmethod
    async def delete_currency(self, currency: CurrencyCode) -> None:
        """Удалить все сохранённые курсы валюты."""
        ...