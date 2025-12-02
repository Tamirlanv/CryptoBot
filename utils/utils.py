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
