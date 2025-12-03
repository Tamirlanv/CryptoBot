from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_kb=ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="🔔 Мои алерты"), KeyboardButton(text="⭐ Топ 10")],
        [KeyboardButton(text="🔥 Тренды"), KeyboardButton(text="💰 Курсы криптовалют")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите опцию..."
)

auth_kb=ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧑‍💻 Вход/Регистрация")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Пройдите регистрацию"
)

VS_LIST = ["usd", "eur", "rub", "kzt", "cny", "try", "gbp", "uah", "jpy", "cad", "chf", "brl"]

def price_keyboard(coin):
    keyboard = []
    row = []
    for vs in VS_LIST:
        row.append(InlineKeyboardButton(
            text=vs.upper(),
            callback_data=f"price:{coin}:{vs}"
        ))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


CRYPTO_LIST = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "doge": "dogecoin",
    "xrp": "ripple",
    "bnb": "binancecoin",
    "ton": "toncoin",
    "ada": "cardano",
    "dot": "polkadot",
    "trx": "tron",
    "ltc": "litecoin",
    "usdt": "tether",
}

def convert_keyboard(from_coin, amount):
    keyboard = []
    row = []
    for coin in CRYPTO_LIST:
        row.append(InlineKeyboardButton(
            text=coin.upper(),
            callback_data=f"convert:{from_coin}:{coin}:{amount}"
        ))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



