"""
Тестовый скрипт для проверки валидации API ключа CoinGecko
Теперь с правильной аутентификацией через headers!
"""
import asyncio
from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI


async def test_validation():
    await cg_client.init()
    
    print("=" * 60)
    print("Тестирование валидации CoinGecko API ключа")
    print("=" * 60)
    print()
    
    # Тест 1: Пустой ключ
    print("✅ Тест 1: Пустой ключ")
    api = CoinGeckoAPI("", cg_client)
    is_valid = await api.validate_api_key()
    print(f"   Результат: {is_valid} (ожидается False)")
    print(f"   Статус: {'✅ PASSED' if not is_valid else '❌ FAILED'}\n")
    
    # Тест 2: Короткий ключ
    print("✅ Тест 2: Короткий ключ")
    api = CoinGeckoAPI("123", cg_client)
    is_valid = await api.validate_api_key()
    print(f"   Результат: {is_valid} (ожидается False)")
    print(f"   Статус: {'✅ PASSED' if not is_valid else '❌ FAILED'}\n")
    
    # Тест 3: Неправильный ключ (длинный)
    print("✅ Тест 3: Неправильный ключ (случайная строка)")
    api = CoinGeckoAPI("wrongkey123456789abcdef", cg_client)
    is_valid = await api.validate_api_key()
    print(f"   Результат: {is_valid} (ожидается False)")
    print(f"   Статус: {'✅ PASSED' if not is_valid else '❌ FAILED'}\n")
    
    # Тест 4: Проверка публичного доступа (без ключа)
    print("✅ Тест 4: Публичный доступ без ключа")
    api_no_key = CoinGeckoAPI("no_key_test_12345", cg_client)
    result = await cg_client.get("/ping")
    print(f"   Публичный /ping ответ: {result}")
    print(f"   Содержит 'gecko_says': {'gecko_says' in result if result else False}\n")
    
    # Тест 5: Валидный ключ
    print("✅ Тест 5: Валидный API ключ")
    print("   Получить ключ можно на: https://www.coingecko.com/en/api/pricing")
    real_key = input("   Введите ваш реальный CoinGecko Demo API ключ (или Enter для пропуска): ")
    if real_key.strip():
        api = CoinGeckoAPI(real_key.strip(), cg_client)
        is_valid = await api.validate_api_key()
        print(f"   Результат: {is_valid} (ожидается True)")
        print(f"   Статус: {'✅ PASSED - Ключ валиден!' if is_valid else '❌ FAILED - Ключ невалиден'}\n")
        
        if is_valid:
            # Тест реального запроса
            print("   Тестируем реальный запрос с валидным ключом...")
            price_data = await api.price("bitcoin", "usd")
            if price_data and "bitcoin" in price_data:
                btc_price = price_data["bitcoin"]["usd"]
                print(f"   💰 Bitcoin цена: ${btc_price:,.2f}")
                print("   ✅ Запрос выполнен успешно!\n")
            else:
                print(f"   ❌ Ошибка при получении цены: {price_data}\n")
    else:
        print("   ⏭️  Пропущено\n")
    
    print("=" * 60)
    print("Тестирование завершено!")
    print("=" * 60)
    
    await cg_client.close()


if __name__ == "__main__":
    asyncio.run(test_validation())
