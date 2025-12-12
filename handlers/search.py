from aiogram import Router, F
from aiogram.types import Message

from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI

router = Router()

@router.message(F.text.startswith("/search"))
async def search_coin(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return await message.answer("Формат: /search <название монеты>\nПример: /search bitcoin")
    
    query = args[1].lower().strip()
    api = CoinGeckoAPI("", cg_client)
    await cg_client.init()
    coins_list = await api.list_coins()
    if not coins_list or "error" in coins_list:
        return await message.answer("Ошибка при поиске монет.")
    
    query_normalized = query.replace("-", " ").replace("_", " ")
    exact_matches = []
    starts_with = []
    contains = []
    for coin in coins_list:
        name = coin.get("name", "").lower()
        symbol = coin.get("symbol", "").lower()
        coin_id = coin.get("id", "").lower()
        name_normalized = name.replace("-", " ").replace("_", " ")
        coin_id_normalized = coin_id.replace("-", " ").replace("_", " ")
        coin_data = (coin.get("name", ""), symbol.upper(), coin.get("id", ""))
        if (name == query or symbol == query or coin_id == query or name_normalized == query_normalized or coin_id_normalized == query_normalized):
            exact_matches.append(coin_data)
        elif (name.startswith(query) or symbol.startswith(query) or coin_id.startswith(query) or name_normalized.startswith(query_normalized) or coin_id_normalized.startswith(query_normalized)):
            starts_with.append(coin_data)
        elif (query in name or query in symbol or query in coin_id or query_normalized in name_normalized or query_normalized in coin_id_normalized):
            contains.append(coin_data)
    results = exact_matches + starts_with + contains
    if not results:
        return await message.answer(f"❌ Монеты с названием '{query}' не найдены.")
    
    text = f"🔍 Результаты поиска для '{query}':\n\n"
    if exact_matches:
        text += "✅ <b>Точное совпадение:</b>\n"
        for i, (name, symbol, coin_id) in enumerate(exact_matches[:3], 1):
            text += f"{i}. {name} ({symbol}) → <code>/coin {coin_id}</code>\n"
        text += "\n"
    remaining = results[len(exact_matches):]
    if remaining:
        text += "📋 <b>Похожие результаты:</b>\n"
        for i, (name, symbol, coin_id) in enumerate(remaining[:7], 1):
            text += f"{i}. {name} ({symbol}) → <code>/coin {coin_id}</code>\n"
    total_found = len(results)
    if total_found > 10:
        text += f"\n<i>Показано 10 из {total_found} результатов</i>"
    await message.answer(text, parse_mode="HTML")
