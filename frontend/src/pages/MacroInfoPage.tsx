import React from "react";
import { Link } from "react-router-dom";

const MacroInfoPage: React.FC = () => (
  <div className="page-single macro-info">
    <div className="glass-card">
      <h2>Факторы валютного курса</h2>
      <section>
        <h3>Ключевые ставки центробанков</h3>
        <p>
          Ставка ЦБ РФ, ФРС США или ЕЦБ — один из сильнейших драйверов. Рост ставки делает
          депозиты в национальной валюте привлекательнее, что поддерживает курс.
        </p>
      </section>
      <section>
        <h3>Цены на сырьё</h3>
        <p>
          Нефть Brent, газ, золото. Для сырьевых экономик рост нефти увеличивает экспортную выручку
          и может укреплять национальную валюту (например, давление на USD/RUB вниз).
        </p>
      </section>
      <section>
        <h3>Инфляция (CPI)</h3>
        <p>
          Показывает обесценивание денег. Устойчиво высокая инфляция на горизонте месяцев ослабляет
          валюту относительно более стабильных экономик.
        </p>
      </section>
      <p>
        <Link to="/" className="pill pill--active">
          ← Смотреть факторы на графике главной
        </Link>
      </p>
    </div>
  </div>
);

export default MacroInfoPage;
