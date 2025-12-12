from aiogram import Router, F
from aiogram.types import Message

from coingecko.coingecko_api import CoinGeckoAPI
from . import client

router = Router()

@router.message(F.text == "📋 Доступные криптовалюты")
async def list_coins(message: Message):
    api = CoinGeckoAPI("", client)
    await client.init()

    coins_list = await api.list_coins()
    if not coins_list or "error" in coins_list:
        return await message.answer("Ошибка при загрузке списка монет.")

    total = len(coins_list)
    text = "📋 <b>Доступные криптовалюты</b>\n\n"
    text += f"Всего монет: {total}\n"
    text += "Показываю первые 50:\n\n"

    for i, coin in enumerate(coins_list[:50], 1):
        name = coin.get("name", "")
        symbol = coin.get("symbol", "").upper()
        coin_id = coin.get("id", "")
        text += f"{i}. {name} ({symbol}) → <code>/coin {coin_id}</code>\n"

    if total > 50:
        text += f"\n… и ещё {total - 50} монет\n"

    text += "\n🔍 Используйте /search &lt;название&gt; для точного поиска"

    await message.answer(text, parse_mode="HTML")
