import asyncio
import logging
from coingecko.coingecko_client import cg_client
from database import add_alert_db, list_alerts_db, remove_alert_db, set_alert_triggered

logger = logging.getLogger(__name__)

alert_manager = None


def set_alert_manager(manager):
    global alert_manager
    alert_manager = manager
    return manager

class AlertManager:
    def __init__(self, cg_client, poll_interval: int = 60):
        self.client = cg_client
        self.poll_interval = poll_interval

    async def start(self, bot):
        await self.client.init()
        self._bot = bot
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.client.close()

    async def _loop(self):
        while True:
            try:
                await self.check_and_notify()
            except Exception as e:
                logger.exception("Alert loop error")
            await asyncio.sleep(self.poll_interval)

    async def check_and_notify(self):
        rows = list_alerts_db()  
        if not rows:
            return
        coins = set(r[2] for r in rows)
        if not coins:
            return
        coins_str = ",".join(coins)
        prices = await self.client.get_price(coins_str, currency="usd")  
        if not prices or "error" in prices:
            return

        for row in rows:
            alert_id, user_id, coin, direction, threshold, currency, triggered = row
            
            if currency == "usd":
                coin_price = prices.get(coin, {}).get("usd")
            else:
                single = await self.api.get_price(coin, currency)
                if "error" in single:
                    continue
                coin_price = single.get(coin, {}).get(currency)

            if coin_price is None:
                continue

            triggered_now = False
            if direction == "above" and coin_price >= threshold:
                triggered_now = True
            if direction == "below" and coin_price <= threshold:
                triggered_now = True

            if triggered_now and not triggered:
            
                try:
                    await self._bot.send_message(user_id, f"⚠️ ALARM: {coin.upper()} is {direction} {threshold} {currency.upper()} — current: {coin_price}")
                except Exception as e:
                    logger.exception("Failed to send alert message")
                set_alert_triggered(alert_id, True)
            
            if (not triggered_now) and triggered:
                set_alert_triggered(alert_id, False)


    def add_alert(self, user_id, coin, direction, threshold, currency="usd"):
        return add_alert_db(user_id, coin, direction, threshold, currency)

    def list_user_alerts(self, user_id):
        rows = list_alerts_db(user_id)
        return rows

    def remove_alert(self, alert_id):
        remove_alert_db(alert_id)
        
        
alert_manager=AlertManager(cg_client)
