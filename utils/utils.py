def format_price(x: float) -> str:
    s = str(x)
    if '.' not in s:
        return s  
    whole, frac = s.split('.', 1)
    frac = frac[:3]
    frac = frac.rstrip('0')
    if frac == "":
        return f"{whole}.0"
    return f"{whole}.{frac}"


VALID_FIAT = {
    "usd", "eur", "rub", "kzt", "gbp",
    "uah", "byr", "cny", "jpy", "krw",
    "try", "aud", "cad", "chf", "pln"
}

def validate_currency(currency: str) -> bool:
    return currency.lower() in VALID_FIAT
