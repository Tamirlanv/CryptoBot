# Валидация API ключей CoinGecko

## Проблема
CoinGecko API предоставляет публичный доступ даже без API ключа. Когда пользователь вводит неправильный ключ, API просто игнорирует его и возвращает данные как для публичного запроса. Это означает, что без валидации бот не может определить, правильный ли ключ ввел пользователь.

**Дополнительная проблема:** Изначально API ключ отправлялся через параметры запроса (`params`), а не через заголовки (`headers`), что является неправильным методом аутентификации для CoinGecko Demo API.

## Решение

### 1. Правильная аутентификация через Headers

Обновлён метод `get_headers()` в классе `CoinGeckoAPI`:

```python
def get_headers(self):
    """Возвращает headers для аутентификации через CoinGecko Demo API"""
    return {
        "accept": "application/json",
        "x-cg-demo-api-key": self.api_key
    }
```

**Важно:** Используется `x-cg-demo-api-key` в headers (рекомендованный метод), а не `x_cg_demo_api-key` в параметрах запроса.

### 2. Обновлён HTTPClient

Добавлена поддержка `headers` во все методы:

```python
async def request(self, method: str, path: str, params=None, headers=None):
    # ...
    async with self.session.request(method, url, params=params, headers=headers) as resp:
        # ...
```

### 3. Метод валидации

Добавлен метод `validate_api_key()` с проверкой через `/ping` endpoint:

```python
async def validate_api_key(self):
    """
    Проверка валидности API ключа через endpoint /ping.
    Возвращает True, если ключ валидный, иначе False.
    """
    # Базовая проверка формата (ключи обычно длинные строки)
    if not self.api_key or len(self.api_key) < 10:
        return False
        
    try:
        # Используем endpoint /ping для проверки с правильными headers
        result = await self.client.get("/ping", headers=self.get_headers())
        
        # Проверяем статус код и наличие gecko_says в ответе
        if result and "error" not in result and "gecko_says" in result:
            return True
        
        # Если получили ошибку 401 - неверный ключ
        if result and result.get("status") == 401:
            return False
            
        return False
    except Exception as e:
        print(f"Ошибка валидации API ключа: {e}")
        return False
```

### 4. Обновлены все методы API

Все методы теперь используют правильную аутентификацию:

```python
# Было (неправильно):
async def price(self, coin, vs):
    params = {
        "ids": coin,
        "vs_currencies": vs,
        **self.auth()  # ключ в параметрах
    }
    return await self.client.get("/simple/price", params)

# Стало (правильно):
async def price(self, coin, vs):
    params = {
        "ids": coin,
        "vs_currencies": vs
    }
    return await self.client.get("/simple/price", params=params, headers=self.get_headers())
```

### 5. Проверка при вводе ключа

В обработчике `cg_got_key` добавлена валидация перед сохранением:

```python
@router.message(CGAuth.waiting_key)
async def cg_got_key(message: Message, state: FSMContext):
    api_key = message.text.strip()
    
    # Индикация проверки
    wait_msg = await message.answer("⏳ Проверяю API ключ...")
    
    # Валидация API ключа
    api = CoinGeckoAPI(api_key, cg_client)
    await cg_client.init()
    
    is_valid = await api.validate_api_key()
    
    await wait_msg.delete()
    
    if not is_valid:
        await message.answer(
            "❌ *Ошибка!* API ключ недействителен.\n\n"
            "Пожалуйста, проверьте ключ и попробуйте снова.\n"
            "Получить ключ можно на: https://www.coingecko.com/en/api/pricing",
            parse_mode="Markdown"
        )
        return
    
    save_cg_key(message.from_user.id, api_key)
    await message.answer(success_text, reply_markup=main_kb)
    await state.clear()
```

## Что проверяется

1. **Базовая проверка формата**: ключ не пустой и длиннее 10 символов
2. **API проверка**: запрос к endpoint `/ping` с API ключом
3. **Обработка ошибок**: если произошла ошибка, ключ считается невалидным

## Почему это работает

- CoinGecko API endpoint `/ping` проверяет валидность ключа
- Правильный ключ вернет успешный ответ
- Неправильный ключ или запрос без ключа вернет ошибку или другой формат ответа

## Тестирование

Запустите `test_validation.py` для проверки:

```bash
python test_validation.py
```

Скрипт проверит:
- Пустой ключ ❌
- Короткий ключ ❌  
- Неправильный ключ ❌
- Ваш реальный ключ ✅

## Пользовательский опыт

**До валидации:**
- Пользователь вводит любую строку
- Бот принимает и сохраняет
- При запросах данные приходят (публичный доступ)
- Пользователь думает, что всё работает

**После валидации:**
- Пользователь вводит ключ
- Показывается "⏳ Проверяю API ключ..."
- Если ключ неверный: "❌ Ошибка! API ключ недействителен"
- Если ключ верный: "✅ Вход успешен!"
- Сохраняется только валидный ключ

## Дополнительные улучшения (опционально)

### Проверка лимитов API ключа
```python
async def check_api_limits(self):
    """Проверка оставшихся лимитов запросов"""
    # CoinGecko возвращает информацию о лимитах в заголовках
    # Можно добавить эту информацию пользователю
    pass
```

### Регулярная проверка ключа
```python
# При каждом запросе проверять, не истек ли ключ
# Уведомлять пользователя о необходимости обновления
```
