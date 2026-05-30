from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from infrastructure.nbrb_client import NbrbApiClient


@pytest.mark.asyncio
async def test_get_rate_divides_by_cur_scale():
    client = NbrbApiClient()
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = {"Cur_OfficialRate": 3.872, "Cur_Scale": 100}

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=response):
        rate = await client.get_rate("RUB", date(2026, 5, 30))

    assert rate.rate == pytest.approx(0.03872)
    assert rate.currency == "RUB"
    await client.close()


@pytest.mark.asyncio
async def test_dynamics_applies_rub_scale_without_cur_scale():
    client = NbrbApiClient()
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = [
        {"Cur_ID": 456, "Date": "2026-05-30T00:00:00", "Cur_OfficialRate": 3.872},
    ]

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=response):
        rates = await client.get_rates_for_period("RUB", date(2026, 5, 30), date(2026, 5, 30))

    assert rates[0].rate == pytest.approx(0.03872)
    await client.close()


@pytest.mark.asyncio
async def test_dynamics_applies_try_scale_without_cur_scale():
    client = NbrbApiClient()
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json.return_value = [
        {"Cur_ID": 460, "Date": "2026-05-30T00:00:00", "Cur_OfficialRate": 0.6012},
    ]

    with patch.object(client._client, "get", new_callable=AsyncMock, return_value=response):
        rates = await client.get_rates_for_period("TRY", date(2026, 5, 30), date(2026, 5, 30))

    assert rates[0].rate == pytest.approx(0.06012)
    await client.close()
