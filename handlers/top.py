from aiogram import Router, F
from aiogram.types import Message

from database import get_cg_key
from coingecko.coingecko_api import CoinGeckoAPI
from utils.utils import format_price
from . import client

router = Router()

@router.message(F.text == "⭐ Топ 10")
async def cg_top(message: Message):
    api_key = get_cg_key(message.from_user.id)
    if not api_key:
        return await message.answer("Сначала введите CoinGecko API Key!")
    client.api_key = api_key
    await client.init()
    api = CoinGeckoAPI(api_key, client)
    data = await api.get_markets("usd", per_page=10, page=1)
    if not data or "error" in data:
        return await message.answer("Ошибка при получении топа.")
    text = "🏆 Топ-10 по рыночной капитализации:\n\n\n"
    for i, coin in enumerate(data, 1):
        change = coin.get('price_change_percentage_24h', 0)
        trend_emoji = "📈" if change >= 0 else "📉"
        text += f"{i}. {coin.get('name')} ({coin.get('symbol').upper()}) — ${format_price(coin.get('current_price'))}: 24h: {change:+.2f}% {trend_emoji}\n"
    await message.answer(text)