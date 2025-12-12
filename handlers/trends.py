from aiogram import Router, F
from aiogram.types import Message

from database import get_cg_key
from coingecko.coingecko_api import CoinGeckoAPI
from . import client

router = Router()

@router.message(F.text == "🔥 Тренды")
async def cg_trending(message: Message):
    api_key = get_cg_key(message.from_user.id)
    if not api_key:
        return await message.answer("Сначала введите CoinGecko API Key!")
    client.api_key = api_key
    await client.init()
    api = CoinGeckoAPI(api_key, client)
    data = await api.get_trending()
    if not data or "error" in data:
        return await message.answer("Ошибка получения трендов.")
    coins = data.get("coins", [])
    text = "🔥 Trending:\n\n"
    for item in coins:
        c = item.get("item", {})
        text += f"- {c.get('name')} ({c.get('symbol').upper()}) — market cap rank: {c.get('market_cap_rank')}\n"
    await message.answer(text)