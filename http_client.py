import aiohttp
import logging
from typing import Optional
from utils.cache import CacheTTL

logger = logging.getLogger(__name__)


class HTTPClient:

    def __init__(self, base_url: str = ""):
        self.base_url = base_url.rstrip("/") + "/" if base_url else ""
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache = CacheTTL()

    async def init(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    async def request(self, method: str, path: str, params=None, headers=None):
        await self.init()

        url = self.base_url + path.lstrip("/")

        cache_key = f"{method}:{url}:{tuple(sorted((params or {}).items()))}:{tuple(sorted((headers or {}).items()))}"

        cached = self.cache.get(cache_key)
        if cached:
            print(f"[CACHE HIT] {cache_key}")
            return cached

        try:
            async with self.session.request(method, url, params=params, headers=headers) as resp:
                text = await resp.text()

                if resp.status >= 400:
                    logger.error(f"HTTP {resp.status}: {text}")
                    return {"error": True, "status": resp.status, "message": text}

                try:
                    data = await resp.json()
                except ValueError:
                    data = text  

                self.cache.set(cache_key, data)
                print(f"[CACHE SET] {cache_key}")
                return data

        except Exception as e:
            logger.exception("Ошибка HTTP запроса")
            return {"error": True, "exception": str(e)}

    async def get(self, path, params=None, headers=None):
        return await self.request("GET", path, params, headers)

    async def post(self, path, params=None, headers=None):
        return await self.request("POST", path, params, headers)

    async def put(self, path, params=None, headers=None):
        return await self.request("PUT", path, params, headers)

    async def delete(self, path, params=None, headers=None):
        return await self.request("DELETE", path, params, headers)
