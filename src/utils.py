from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

def to_cents(amount_str):
    try:
        return int((Decimal(amount_str) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, TypeError):
        raise ValueError()

def format_cents(cents):
    return f"{cents / 100:.2f}"

def normalize_username(username):
    return username.lower().strip()