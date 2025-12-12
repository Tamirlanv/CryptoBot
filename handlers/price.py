from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database import get_cg_key
from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI
from utils.utils import format_price
from keyboards import price_keyboard

router = Router()

@router.message(F.text.startswith("/price"))
async def cg_price(message: Message):
    text_parts = message.text.split()
    if len(text_parts) < 3:
        return await message.answer("Формат: /price <монета> <валюта>\nПример: /price bitcoin usd или /price bitcoin-cash usd")
    
    vs = text_parts[-1].lower().strip()
    coin = " ".join(text_parts[1:-1]).lower().strip()
    coin = coin.replace(" ", "-")
    
    api_key = get_cg_key(message.from_user.id)
    if not api_key:
        return await message.answer("Сначала введите CoinGecko API Key!")
    api = CoinGeckoAPI(api_key, cg_client)
    await cg_client.init()
    data = await api.price(coin, vs)
    if not data or "error" in data:
        return await message.answer("Ошибка API или монета не найдена.")
    price = data.get(coin, {}).get(vs)
    if price is None:
        return await message.answer("Пара не поддерживается.")
    await message.answer(f"💰 {coin.upper()} → {vs.upper()} = {format_price(price)}",
                         reply_markup=price_keyboard(coin))
    
    
@router.callback_query(F.data.startswith("price"))
async def price_callback(callback: CallbackQuery):
    _, coin, vs = callback.data.split(":")

    api_key = get_cg_key(callback.from_user.id)
    api = CoinGeckoAPI(api_key, cg_client)
    await cg_client.init()
    data = await api.price(coin, vs)

    price = data.get(coin, {}).get(vs)
    if price is None:
        return await callback.message.edit_text("Пара не поддерживается.")

    await callback.message.edit_text(
        f"💰 {coin.upper()} → {vs.upper()} = {format_price(price)}",
        reply_markup=price_keyboard(coin)
    )
