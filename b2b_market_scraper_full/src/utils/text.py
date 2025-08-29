import re
from typing import Optional, Tuple

CURRENCY_SYMBOLS = {
    '₹': 'INR', 'Rs': 'INR', 'INR': 'INR',
    '$': 'USD', 'USD': 'USD',
    '€': 'EUR', 'EUR': 'EUR'
}

def clean_whitespace(s: str) -> str:
    return re.sub(r'\s+', ' ', s or '').strip()

def extract_price(raw: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Extract min/max price and currency from a messy price string.
    Examples:
      '₹ 5,000 - ₹ 7,500 / Piece' -> (5000.0, 7500.0, 'INR')
      '$2.5 - $3.1 / kg' -> (2.5, 3.1, 'USD')
      '₹ 12,000 / Unit' -> (12000.0, 12000.0, 'INR')
    """
    if not raw:
        return None, None, None
    s = clean_whitespace(raw)
    # Currency
    currency = None
    for sym, code in CURRENCY_SYMBOLS.items():
        if sym in s:
            currency = code
            s = s.replace(sym, '')
    # Numbers
    nums = re.findall(r"\d+[\d,]*\.?\d*", s)
    vals = []
    for n in nums:
        n = n.replace(',', '')
        try:
            vals.append(float(n))
        except ValueError:
            pass
    if not vals:
        return None, None, currency
    if len(vals) == 1:
        return vals[0], vals[0], currency
    return min(vals), max(vals), currency
