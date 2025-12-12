from .coingecko_client import cg_client

class CoinGeckoAPI:

    def __init__(self, api_key: str, cg_client):
        self.api_key = api_key
        self.client = cg_client
        
    def get_headers(self):
        return {
            "accept": "application/json",
            "x-cg-demo-api-key": self.api_key
        }
    
    async def validate_api_key(self):
        if not self.api_key or len(self.api_key) < 10:
            return False
            
        try:
            result = await self.client.get("/ping", headers=self.get_headers())
            
            if result and "error" not in result and "gecko_says" in result:
                return True
            
            if result and result.get("status") == 401:
                return False
                
            return False
        except Exception as e:
            print(f"Ошибка валидации API ключа: {e}")
            return False

    async def price(self, coin, vs):
        params = {
            "ids": coin,
            "vs_currencies": vs
        }
        return await self.client.get("/simple/price", params=params, headers=self.get_headers())

    async def list_coins(self):
        return await self.client.get("/coins/list", headers=self.get_headers())
    
    async def get_currencies(self):
        return await self.client.get("simple/supported_vs_currencies")

    async def get_trending(self):
        return await self.client.get("search/trending")

    async def get_markets(self, vs_currency="usd", per_page=10, page=1):
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page
        }
        return await self.client.get("coins/markets", params=params, headers=self.get_headers())

    async def get_coin(self, coin_id):
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false"
        }
        return await self.client.get(f"coins/{coin_id}", params=params, headers=self.get_headers())

    async def get_chart(self, coin, currency="usd", days=7):
        params = {"vs_currency": currency, "days": days}
        return await self.client.get(
            f"coins/{coin}/market_chart",
            params=params,
            headers=self.get_headers()
        )

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