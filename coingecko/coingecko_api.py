from .coingecko_client import cg_client

class CoinGeckoAPI:

    def __init__(self, api_key: str, cg_client):
        self.api_key = api_key
        self.client = cg_client
        
    def auth(self):
        return {"x_cg_demo_api-key": self.api_key}

    async def price(self, coin, vs):
        params = {
            "ids": coin,
            "vs_currencies": vs,
            **self.auth()
        }
        return await self.client.get("/simple/price", params)

    async def list_coins(self):
        return await self.client.get("/coins/list", self.auth())
    
    async def get_currencies(self):
        return await self.client.get("simple/supported_vs_currencies")

    async def get_trending(self):
        return await self.client.get("search/trending")

    async def get_markets(self, vs_currency="usd", per_page=10, page=1):
        return await self.client.get(
            "coins/markets",
            {
                "vs_currency": vs_currency,
                "order": "market_cap_desc",
                "per_page": per_page,
                "page": page
            }
        )

    async def get_coin(self, coin_id):
        return await self.client.get(
            f"coins/{coin_id}",
            {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false"
            }
        )

    async def get_chart(self, coin, currency="usd", days=7):
        return await self.client.get(
            f"coins/{coin}/market_chart",
            {"vs_currency": currency, "days": days}
        )

    # ---------- КОНВЕРТЕР ----------
    async def convert(self, from_coin: str, to_coin: str, amount: float):
        p1 = await self.price(from_coin, "usd")
        if not p1 or from_coin not in p1 or "usd" not in p1[from_coin]:
            return {"error": True}

        p2 = await self.price(to_coin, "usd")
        if not p2 or to_coin not in p2 or "usd" not in p2[to_coin]:
            return {"error": True}

        usd1 = p1[from_coin]["usd"]
        usd2 = p2[to_coin]["usd"]

        rate = usd1 / usd2

        return {
            "rate": rate,
            "result": rate * amount,
            "from_usd": usd1,
            "to_usd": usd2
        }

    
    
    
