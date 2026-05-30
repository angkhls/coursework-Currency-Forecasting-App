from typing import List, Literal

import httpx

from domain.models import NewsArticle

NewsCategory = Literal["forex", "general", "crypto", "merger"]

FINNHUB_NEWS_URL = "https://finnhub.io/api/v1/news"


class FinnhubClient:
    def __init__(self, api_key: str):
        self._api_key = api_key.strip()

    async def get_market_news(self, category: NewsCategory = "general") -> List[NewsArticle]:
        if not self._api_key:
            raise ValueError(
                "FINNHUB_API_KEY не задан. Получите ключ на https://finnhub.io/register "
                "и добавьте в forecasting/.env"
            )

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                FINNHUB_NEWS_URL,
                params={"category": category, "token": self._api_key},
            )
            response.raise_for_status()
            payload = response.json()

        if not isinstance(payload, list):
            raise ValueError("Неожиданный ответ Finnhub")

        articles: List[NewsArticle] = []
        for item in payload[:50]:
            if not isinstance(item, dict):
                continue
            headline = str(item.get("headline") or "").strip()
            if not headline:
                continue
            articles.append(
                NewsArticle(
                    id=int(item.get("id") or 0),
                    headline=headline,
                    summary=str(item.get("summary") or "")[:500],
                    source=str(item.get("source") or "Finnhub"),
                    url=str(item.get("url") or ""),
                    image=str(item.get("image") or "") or None,
                    category=str(item.get("category") or category),
                    datetime=int(item.get("datetime") or 0),
                )
            )
        return articles
