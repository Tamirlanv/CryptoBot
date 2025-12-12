from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_cg_key, save_cg_key
from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI
from keyboards import auth_kb, main_kb

router = Router()

success_text = (
    "Вход успешен!\n\n"
    "Теперь вы можете пользоваться функционалом бота.\n"
    "Доступные команды:\n\n"
    "💰 Цены и конвертация\n"
    "/price <монета> <валюта> — цена монеты\n"
    "/convert <из> <в> <количество> — конвертация валют\n\n"
    "🏆 Информация о рынке\n"
    "/coin <id> — подробная информация о монете\n"
    "⏰ Алерты\n"
    "/alert <монета> <выше/ниже> <значение> [валюта] — создать алерт\n"
    "/alert_remove <id> — удалить алерт\n\n"
    "Теперь можно начинать!"
)

class CGAuth(StatesGroup):
    waiting_key = State()

@router.message(F.text == "🧑‍💻 Вход/Регистрация")
async def cg_start(message: Message, state: FSMContext):
    key = get_cg_key(message.from_user.id)
    if key:
        return await message.answer(success_text, reply_markup=main_kb)
    await message.answer("Введите ваш CoinGecko Demo API Key:")
    await state.set_state(CGAuth.waiting_key)

@router.message(CGAuth.waiting_key)
async def cg_got_key(message: Message, state: FSMContext):
    api_key = message.text.strip()
    
    wait_msg = await message.answer("⏳ Проверяю API ключ...")
    
    api = CoinGeckoAPI(api_key, cg_client)
    await cg_client.init()
    
    is_valid = await api.validate_api_key()
    
    await wait_msg.delete()
    
    if not is_valid:
        await message.answer(
            "❌ Ошибка! API ключ недействителен.\n\n"
            "Пожалуйста, проверьте ключ и попробуйте снова.\n"
            "Получить ключ можно на: https://www.coingecko.com/en/api/pricing",
            parse_mode="Markdown"
        )
        return
    
    save_cg_key(message.from_user.id, api_key)
    await message.answer(success_text, reply_markup=main_kb)
    await state.clear()
    await state.clear()