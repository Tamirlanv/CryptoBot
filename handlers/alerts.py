from aiogram import Router, F
from aiogram.types import Message

from database import list_alerts_db, remove_alert_db, add_alert_db, get_cg_key
from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI
from utils.utils import format_price

router = Router()

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
            "/alert монета выше/ниже цена [валюта]\n"
            "Пример: /alert bitcoin выше 70000 usd"
        )
    coin = args[1].lower()
    direction_raw = args[2].lower()
    mapping = {
        "выше": "выше",
        "ниже": "ниже",
        "вверх": "выше",
        "вниз": "ниже",
        "above": "выше",
        "below": "ниже"
    }
    direction = mapping.get(direction_raw)
    if not direction:
        return await message.answer("Направление должно быть: выше или ниже (поддерживаются также: вверх/вниз, above/below).")
    try:
        threshold = float(args[3])
    except:
        return await message.answer("Неверное значение цены.")
    currency = args[4].lower() if len(args) > 4 else "usd"
    
    api_key = get_cg_key(message.from_user.id)
    api = CoinGeckoAPI(api_key if api_key else "", cg_client)
    await cg_client.init()
    
    wait_msg = await message.answer("⏳ Проверяю монету...")
    validation = await api.price(coin, currency)
    await wait_msg.delete()
    
    if not validation or "error" in validation or coin not in validation:
        return await message.answer(
            f"❌ Монета '{coin}' не найдена в CoinGecko или валюта '{currency}' не поддерживается.\n\n"
            "Проверьте правильность написания.\n"
            "Пример: bitcoin, ethereum, solana"
        )
    
    alert_id = add_alert_db(
        message.from_user.id,
        coin,
        direction,
        threshold,
        currency
    )
    current_price = validation[coin][currency]
    await message.answer(
        f"🔔 Алерт создан!\n"
        f"ID: {alert_id}\n"
        f"Монета: {coin.upper()}\n"
        f"Текущая цена: {format_price(current_price)} {currency.upper()}\n"
        f"Условие: {direction} {threshold} {currency.upper()}"
    )