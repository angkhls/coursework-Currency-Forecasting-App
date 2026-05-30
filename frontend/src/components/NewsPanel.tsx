import React, { useEffect, useState } from "react";
import { currencyApi } from "../api/client";
import type { NewsFeed } from "../types";

function formatNewsDate(ts: number): string {
  if (!ts) return "";
  return new Date(ts * 1000).toLocaleString("ru-RU", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

interface Props {
  compact?: boolean;
}

const NewsPanel: React.FC<Props> = ({ compact }) => {
  const [feed, setFeed] = useState<NewsFeed | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await currencyApi.getNews();
        if (!cancelled) setFeed(data);
      } catch (e: unknown) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Не удалось загрузить новости");
          setFeed(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className={compact ? "news-panel news-panel--compact" : "news-panel"}>
      <div className="news-panel__header">
        <h2>{compact ? "Новости" : "Новости рынка"}</h2>
      </div>

      {error && <div className="alert alert--error">{error}</div>}
      {loading && <p className="loading">Загрузка новостей…</p>}

      {!loading && feed && (
        <>
          <p className="news-panel__note">{feed.source_note}</p>
          <ul className="news-list">
            {feed.articles.map((article) => (
              <li key={article.id || article.headline} className="news-card glass-card">
                {article.image && (
                  <img
                    className="news-card__img"
                    src={article.image}
                    alt=""
                    loading="lazy"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = "none";
                    }}
                  />
                )}
                <div className="news-card__body">
                  <div className="news-card__meta">
                    <span>{article.source}</span>
                    <span>{formatNewsDate(article.datetime)}</span>
                  </div>
                  <h3 className="news-card__title">
                    {article.url ? (
                      <a href={article.url} target="_blank" rel="noopener noreferrer">
                        {article.headline}
                      </a>
                    ) : (
                      article.headline
                    )}
                  </h3>
                  {article.summary && <p className="news-card__summary">{article.summary}</p>}
                </div>
              </li>
            ))}
          </ul>
          {feed.articles.length === 0 && !error && (
            <p className="news-panel__empty">Нет статей.</p>
          )}
        </>
      )}
    </section>
  );
};

export default NewsPanel;
