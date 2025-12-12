import asyncio
from database import list_alerts_db, set_alert_triggered, get_cg_key
from coingecko.coingecko_api import CoinGeckoAPI
from coingecko.coingecko_client import cg_client

async def alerts_worker(bot):
    while True:
        alerts = list_alerts_db()

        for alert in alerts:
            alert_id, user_id, coin, direction, threshold, currency, triggered = alert

            if triggered:
                continue

            key = get_cg_key(user_id)
            if not key:
                continue

            api = CoinGeckoAPI(key, cg_client)
            await cg_client.init()

            price_data = await api.price(coin, currency)
            if not price_data or "error" in price_data:
                continue

            price = price_data.get(coin, {}).get(currency)
            if price is None:
                continue

            if direction == "above" and price >= threshold:
                await bot.send_message(user_id, f"🔔 {coin.upper()} поднялся ABOVE {threshold} {currency}.\nТекущая цена: {price}")
                set_alert_triggered(alert_id, True)

            if direction == "below" and price <= threshold:
                await bot.send_message(user_id, f"🔔 {coin.upper()} опустился BELOW {threshold} {currency}.\nТекущая цена: {price}")
                set_alert_triggered(alert_id, True)

        await asyncio.sleep(15)
