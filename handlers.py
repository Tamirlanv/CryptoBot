from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import *
from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI
from utils.utils import format_price
from keyboards import *


router = Router()


success_text = (
    "Вход успешен!\n\n"
    "Теперь вы можете пользоваться функционалом бота.\n"
    "Доступные команды:\n\n"
    "💰 *Цены и конвертация*\n"
    "/price <монета> <валюта> — цена монеты\n"
    "/convert <из> <в> <количество> — конвертация валют\n\n"
    "🏆 *Информация о рынке*\n"
    "/coin <id> — подробная информация о монете\n"
    "⏰ *Алерты*\n"
    "/alert <монета> <выше/ниже> <значение> [валюта] — создать алерт\n"
    "/alert_remove <id> — удалить алерт\n\n"
    "Теперь можно начинать!"
)

client=cg_client



@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(f"Привет {message.from_user.full_name}\n"
                         "Я бот трекер криптовалют и имею следующий функционал\n"
                         "Чтобы начать регистрацию пожалуйста нажмите кнопку ниже",
                         reply_markup=auth_kb)



class CGAuth(StatesGroup):
    waiting_key = State()

# ---------------- AUTH ----------------
@router.message(F.text == "🧑‍💻 Вход/Регистрация")
async def cg_start(message: Message, state: FSMContext):
    key = get_cg_key(message.from_user.id)
    if key:
        return await message.answer(success_text, reply_markup=main_kb)
    await message.answer("Введите ваш CoinGecko Demo API Key:")
    await state.set_state(CGAuth.waiting_key)

@router.message(CGAuth.waiting_key)
async def cg_got_key(message: Message, state: FSMContext):
    save_cg_key(message.from_user.id, message.text.strip())
    await message.answer(success_text, reply_markup=main_kb)
    await state.clear()

# ---------------- PRICE ----------------
@router.message(F.text.startswith("/price"))
async def cg_price(message: Message):
    args = message.text.split()
    if len(args) != 3:
        return await message.answer("Формат: /price bitcoin usd")
    coin, vs = args[1].lower(), args[2].lower()
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

# ---------------- CONVERT ----------------
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
        f"💱 {amount} {from_coin.upper()} = {format_price(data['result'])} {to_coin.upper()}",
        reply_markup=convert_keyboard(from_coin, amount)
    )
    
    
@router.callback_query(F.data.startswith("convert"))
async def convert_callback(callback: CallbackQuery):
    _, from_coin, to_coin, amount = callback.data.split(":")
    amount = float(amount)

    api_key = get_cg_key(callback.from_user.id)
    api = CoinGeckoAPI(api_key, cg_client)
    await cg_client.init()

    data = await api.convert(from_coin, to_coin, amount)

    await callback.message.edit_text(
        f"💱 {amount} {from_coin.upper()} = {format_price(data['result'])} {to_coin.upper()}",
        reply_markup=convert_keyboard(from_coin, amount)
    )


# ---------------- TOP ----------------
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
    text = "🏆 Топ-10 по рыночной капитализации:\n"
    for i, coin in enumerate(data, 1):
        text += f"{i}. {coin.get('name')} ({coin.get('symbol').upper()}) — ${format_price(coin.get('current_price'))} — 24h: {coin.get('price_change_percentage_24h'):.2f}%\n"
    await message.answer(text)

# ---------------- COIN INFO ----------------
@router.message(F.text.startswith("/coin"))
async def cg_coin(message: Message):
    args = message.text.split()
    if len(args) != 2:
        return await message.answer("Формат: /coin <id>\nПример: /coin bitcoin")
    coin_id = args[1].lower()
    api_key = get_cg_key(message.from_user.id)
    if not api_key:
        return await message.answer("Сначала введите CoinGecko API Key!")
    client.api_key = api_key
    await client.init()
    api = CoinGeckoAPI(api_key, client)
    data = await api.get_coin(coin_id)
    if not data or "error" in data:
        return await message.answer("Ошибка/монета не найдена.")
    md = data.get("market_data", {})
    price = md.get("current_price", {}).get("usd")
    cap = md.get("market_cap", {}).get("usd")
    vol = md.get("total_volume", {}).get("usd")
    change24 = md.get("price_change_percentage_24h")
    desc = data.get("description", {}).get("en") or ""
    short_desc = (desc[:300] + "...") if desc and len(desc) > 300 else desc
    text = f"🪙 {data.get('name')} ({data.get('symbol').upper()})\nPrice: ${price}\nMarket cap: ${cap}\n24h volume: ${vol}\n24h change: {change24}%\n\n{short_desc}"
    await message.answer(text)

# ---------------- TRENDING ----------------
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
    text = "🔥 Trending:\n"
    for item in coins:
        c = item.get("item", {})
        text += f"- {c.get('name')} ({c.get('symbol').upper()}) — market cap rank: {c.get('market_cap_rank')}\n"
    await message.answer(text)

# ---------------- ALERTS ----------------

@router.message(F.text == "🔔 Мои алерты")
async def my_alerts(message: Message):
    alerts = list_alerts_db(message.from_user.id)
    if not alerts:
        return await message.answer("У вас нет активных алертов.")
    text = "🔔 Ваши алерты:\n\n"
    for id, coin, direction, threshold, currency, triggered in alerts:
        text += (
            f"#{id}: {coin.upper()} — {direction} {threshold} {currency.upper()} "
            f"{'✅ СРАБОТАЛ' if triggered else ''}\n"
        )
    await message.answer(text)
    
    
@router.message(F.text.startswith("/alert_remove"))
async def alert_remove(message: Message):
    args = message.text.split()
    if len(args) != 2:
        return await message.answer("Формат: /alert_remove <id>")
    try:
        alert_id = int(args[1])
    except:
        return await message.answer("ID должен быть числом.")
    remove_alert_db(alert_id)
    await message.answer(f"🗑 Алерт #{alert_id} удалён.")
    

@router.message(F.text.startswith("/alert"))
async def alert_create(message: Message):
    args = message.text.split()
    if len(args) < 4:
        return await message.answer(
            "Формат:\n"
            "/alert <монета> <above/below> <цена> [валюта]\n"
            "Пример: /alert bitcoin выше 70000 usd"
        )
    coin = args[1].lower()
    direction = args[2].lower()
    if direction not in ("выше", "ниже"):
        return await message.answer("Напишите 'выше' или 'ниже'.")
    try:
        threshold = float(args[3])
    except:
        return await message.answer("Неверное значение цены.")
    currency = args[4].lower() if len(args) > 4 else "usd"
    alert_id = add_alert_db(
        message.from_user.id,
        coin,
        "above" if direction == "выше" else "below",
        threshold,
        currency
    )
    await message.answer(
        f"🔔 Алерт создан!\nID: {alert_id}\nМонета: {coin}\nУсловие: {direction} {threshold} {currency}"
    )






