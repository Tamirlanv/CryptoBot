"""
Быстрый тест валидации (без интерактивного ввода)
"""
import asyncio
from coingecko.coingecko_client import cg_client
from coingecko.coingecko_api import CoinGeckoAPI


async def quick_test():
    await cg_client.init()
    
    print("🚀 Быстрый тест валидации CoinGecko API")
    print()
    
    tests = [
        ("Пустой ключ", "", False),
        ("Короткий ключ", "123", False),
        ("Неправильный ключ", "wrongkey123456789abcdef", False),
    ]
    
    passed = 0
    failed = 0
    
    for name, key, expected in tests:
        api = CoinGeckoAPI(key, cg_client)
        result = await api.validate_api_key()
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
            
        print(f"{status} {name}: {result} (ожидалось {expected})")
    
    print()
    print(f"📊 Результаты: {passed} пройдено, {failed} провалено")
    
    if failed == 0:
        print("🎉 Все тесты пройдены успешно!")
    
    await cg_client.close()


if __name__ == "__main__":
    asyncio.run(quick_test())
