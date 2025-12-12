import asyncio
from database import list_alerts_db, set_alert_triggered
from coingecko.coingecko_api import CoinGeckoAPI
from coingecko.coingecko_client import cg_client

async def alerts_worker(bot):
    while True:
        alerts = list_alerts_db()

        for alert in alerts:
            alert_id, user_id, coin, direction, threshold, currency, triggered = alert

            if triggered:
                continue

            api = CoinGeckoAPI("", cg_client)
            await cg_client.init()

            price_data = await api.price(coin, currency)
            if not price_data or "error" in price_data:
                continue

            price = price_data.get(coin, {}).get(currency)
            if price is None:
                continue

            if direction == "выше" and price >= threshold:
                await bot.send_message(user_id, f"🔔 {coin.upper()} поднялся ВЫШЕ {threshold} {currency}.\nТекущая цена: {price}")
                set_alert_triggered(alert_id, True)

            if direction == "ниже" and price <= threshold:
                await bot.send_message(user_id, f"🔔 {coin.upper()} опустился НИЖЕ {threshold} {currency}.\nТекущая цена: {price}")
                set_alert_triggered(alert_id, True)

        await asyncio.sleep(15)
