from aiogram import Router, F
from aiogram.types import Message

from database import get_cg_key
from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI
from utils.utils import format_price

router = Router()

@router.message(F.text.startswith("/convert"))
async def cg_convert(message: Message):
    args = message.text.split()
    if len(args) != 4:
        return await message.answer("Формат: /convert <from> <to> <amount>")

    from_coin, to_coin = args[1].lower(), args[2].lower()
    amount = float(args[3])

    api_key = get_cg_key(message.from_user.id)
    api = CoinGeckoAPI(api_key, cg_client)
    await cg_client.init()

    data = await api.convert(from_coin, to_coin, amount)

    await message.answer(
        f"💱 {amount} {from_coin.upper()} = {format_price(data['result'])} {to_coin.upper()}")