from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import save_cg_key, get_cg_key
from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI
from utils.utils import format_price
from alert_manager import alert_manager 

router = Router()


main_kb=ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="💰 Курсы криптовалют")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите опцию..."
)


success_text = (
    "🔑 Ключ сохранён!\n\n"
    "Теперь вы можете пользоваться функционалом бота.\n"
    "Доступные команды:\n\n"
    "💰 *Цены и конвертация*\n"
    "/price <coin> <vs_currency> — цена монеты\n"
    "/convert <from> <to> <amount> — конвертация валют\n\n"
    "🏆 *Информация о рынке*\n"
    "/top — топ-10 криптовалют\n"
    "/coin <id> — подробная информация о монете\n"
    "/trending — трендовые монеты\n\n"
    "⏰ *Алерты*\n"
    "/alert <coin> <above|below> <value> [currency] — создать алерт\n"
    "/alerts — список ваших алертов\n"
    "/alert_remove <id> — удалить алерт\n\n"
    "Теперь можно начинать!"
)

client=cg_client



@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(f"Привет {message.from_user.full_name}\n"
                         "Я бот трекер криптовалют и имею следующий функционал\n"
                         "Чтобы начать регистрацию пожалуйста нажмите кнопку ниже",
                         reply_markup=main_kb)



class CGAuth(StatesGroup):
    waiting_key = State()

# ---------------- AUTH ----------------
@router.message(F.text == "💰 Курсы криптовалют")
async def cg_start(message: Message, state: FSMContext):
    key = get_cg_key(message.from_user.id)
    if key:
        return await message.answer(success_text)
    await message.answer("Введите ваш CoinGecko Demo API Key:")
    await state.set_state(CGAuth.waiting_key)

@router.message(CGAuth.waiting_key)
async def cg_got_key(message: Message, state: FSMContext):
    save_cg_key(message.from_user.id, message.text.strip())
    await message.answer(success_text)
    await state.clear()

# ---------------- PRICE ----------------
@router.message(F.text.startswith("/price"))
async def cg_price(message: Message):
    args = message.text.split()
    if len(args) != 3:
        return await message.answer("Формат: /price bitcoin usd")
    coin, vs = args[1], args[2]
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
    await message.answer(f"💰 {coin.upper()} → {vs.upper()} = {format_price(price)}")

# ---------------- CONVERT ----------------
@router.message(F.text.startswith("/convert"))
async def cg_convert(message: Message):
    args = message.text.split()
    if len(args) != 4:
        return await message.answer("Формат: /convert <from> <to> <amount>\nПример: /convert bitcoin tether 0.5")
    from_coin, to_coin = args[1].lower(), args[2].lower()
    try:
        amount = float(args[3])
    except:
        return await message.answer("Неверное количество.")
    api_key = get_cg_key(message.from_user.id)
    if not api_key:
        return await message.answer("Сначала введите CoinGecko API Key!")
    api = CoinGeckoAPI(api_key, cg_client)
    await cg_client.init()
    data = await api.convert(from_coin, to_coin, amount)
    if not data or "error" in data:
        return await message.answer("Монета не найдена или ошибка API.")
    await message.answer(
        f"💱 {amount} {from_coin.upper()} = {format_price(data['result'])} {to_coin.upper()}\n"
    )

# ---------------- TOP ----------------
@router.message(F.text == "/top")
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
@router.message(F.text == "/trending")
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
@router.message(F.text == "/alert")
async def cg_alert(message: Message):
    parts = message.text.split()
    if len(parts) not in (4,5):
        return await message.answer("Формат: /alert <coin> <above|below> <threshold> [currency]\nПример: /alert bitcoin above 90000 usd")
    coin = parts[1].lower()
    direction = parts[2].lower()
    if direction not in ("above","below"):
        return await message.answer("direction must be 'above' or 'below'")
    try:
        threshold = float(parts[3])
    except:
        return await message.answer("Неверный threshold")
    currency = parts[4].lower() if len(parts)==5 else "usd"
    user_id = message.from_user.id
    api_key = get_cg_key(user_id)
    if not api_key:
        return await message.answer("Сначала введите CoinGecko API Key!")
    if not alert_manager:
        return await message.answer("Alert manager not ready, попробуйте позже.")
    alert_id = alert_manager.add_alert(user_id, coin, direction, threshold, currency)
    await message.answer(f"✅ Алерт добавлен (id={alert_id}): {coin} {direction} {threshold} {currency}")

@router.message(F.text == "/alerts")
async def cg_list_alerts(message: Message):
    user_id = message.from_user.id
    rows = alert_manager.list_user_alerts(user_id)
    if not rows:
        return await message.answer("У вас нет активных алертов.")
    text = "Ваши алерты:\n"
    for r in rows:
        aid, coin, direction, threshold, currency, triggered = r
        text += f"id={aid}: {coin} {direction} {threshold} {currency} triggered={bool(triggered)}\n"
    await message.answer(text)

@router.message(F.text.startswith("/alert_remove"))
async def cg_remove_alert(message: Message):
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("Формат: /alert_remove <id>")
    try:
        aid = int(parts[1])
    except:
        return await message.answer("id должен быть числом")
    alert_manager.remove_alert(aid)
    await message.answer(f"✅ Алерт {aid} удалён.")


