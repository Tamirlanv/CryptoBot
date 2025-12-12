from aiogram import Router, F
from aiogram.types import Message

from database import get_cg_key
from coingecko.coingecko_api import CoinGeckoAPI
from utils.utils import format_price
from . import client

router = Router()

@router.message(F.text.startswith("/coin"))
async def cg_coin(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) != 2:
        return await message.answer("Формат: /coin <id>\nПример: /coin bitcoin или /coin bitcoin-cash\n\nИспользуйте /search <название> для поиска правильного ID монеты")
    coin_id = args[1].lower().strip()
    api_key = get_cg_key(message.from_user.id)
    if not api_key:
        return await message.answer("Сначала введите CoinGecko API Key!")
    client.api_key = api_key
    await client.init()
    api = CoinGeckoAPI(api_key, client)
    data = await api.get_coin(coin_id)
    if not data or "error" in data:
        return await message.answer(
            f"❌ Монета с ID '{coin_id}' не найдена.\n\n"
            "Используйте /search <название> для поиска правильного ID\n"
            "Пример: /search terra"
        )
    md = data.get("market_data", {})
    price = md.get("current_price", {}).get("usd")
    cap = md.get("market_cap", {}).get("usd")
    vol = md.get("total_volume", {}).get("usd")
    change24 = md.get("price_change_percentage_24h")
    desc = data.get("description", {}).get("en") or ""
    short_desc = (desc[:300] + "...") if desc and len(desc) > 300 else desc
    
    image_data = data.get("image", {})
    image_url = None
    if isinstance(image_data, dict):
        image_url = image_data.get("large") or image_data.get("small") or image_data.get("thumb")
    elif isinstance(image_data, str):
        image_url = image_data
    
    text = f"🪙 <b>{data.get('name')}</b> ({data.get('symbol').upper()})\n\n💵 Цена: ${format_price(price)}\n\n📊 Market cap: ${format_price(cap)}\n\n📈 24h volume: ${format_price(vol)}\n\n📉 24h change: {change24:.2f}%\n\n{short_desc}"
    
    if image_url:
        await message.answer_photo(
            photo=image_url,
            caption=text,
            parse_mode="HTML"
        )
    else:
        await message.answer(text, parse_mode="HTML")