def format_price(x: float) -> str:
    return f"{x:.3f}".rstrip('0').rstrip('.')


VALID_FIAT = {
    "usd", "eur", "rub", "kzt", "gbp",
    "uah", "byr", "cny", "jpy", "krw",
    "try", "aud", "cad", "chf", "pln"
}

def validate_currency(currency: str) -> bool:
    return currency.lower() in VALID_FIAT

