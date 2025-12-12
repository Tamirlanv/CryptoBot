from aiogram import Router, F
from aiogram.types import Message

from database import get_cg_key
from coingecko.coingecko_api import CoinGeckoAPI
from utils.utils import format_price
from . import client

router = Router()

@router.message(F.text == "💰 Курсы криптовалют")
async def get_cryptos(message: Message):
    user_id = message.from_user.id
    api_key = get_cg_key(user_id)
    if not api_key:
        api_key = ""
    client.api_key = api_key
    await client.init()
    api = CoinGeckoAPI(api_key, client)
    data = await api.get_markets(vs_currency="usd", per_page=30, page=1)
    if not data or "error" in data:
        return await message.answer("Ошибка загрузки данных от CoinGecko.")
    
    text = "💰 <b>Топ-30 криптовалют</b>\n\n"
    first_image = None
    
    for i, coin in enumerate(data, 1):
        name = coin.get("name")
        symbol = coin.get("symbol", "").upper()
        price = coin.get("current_price")
        image_url = coin.get("image")
        
        if i == 1 and image_url:
            first_image = image_url
        
        price_f = format_price(price) if price is not None else "—"
        text += f"{i}. <b>{name}</b> ({symbol}): ${price_f} 💵\n\n"
    
    if first_image:
        await message.answer_photo(
            photo=first_image,
            caption=text,
            parse_mode="HTML"
        )
    else:
        await message.answer(text, parse_mode="HTML")
