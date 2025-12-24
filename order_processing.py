# Константы
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
COUPON_SAVE10 = "SAVE10"
COUPON_SAVE20 = "SAVE20"
COUPON_VIP = "VIP"
SAVE10_DISCOUNT_RATE = 0.10
SAVE20_DISCOUNT_RATE = 0.20
SAVE20_SMALL_ORDER_RATE = 0.05
SAVE20_TRIGGER = 200
VIP_DISCOUNT_LARGE = 50
VIP_DISCOUNT_SMALL = 10
VIP_TRIGGER = 100

def parse_request(request: dict):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


def validate_request(user_id, items: list, currency):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if currency is None:
        currency = DEFAULT_CURRENCY

    if len(items) == 0:
        raise ValueError("items must not be empty")

    for it in items:
        if "price" not in it or "qty" not in it:
            raise ValueError("item must have price and qty")
        if it["price"] <= 0:
            raise ValueError("price must be positive")
        if it["qty"] <= 0:
            raise ValueError("qty must be positive")
    
    return currency


def calculate_subtotal(items):
    subtotal = 0
    for it in items:
        subtotal = subtotal + it["price"] * it["qty"]
    return subtotal


def calculate_discount(coupon, subtotal):
    discount = 0
    if coupon is None or coupon == "":
        discount = 0
    elif coupon == "SAVE10":
        discount = int(subtotal * SAVE10_DISCOUNT_RATE)
    elif coupon == "SAVE20":
        if subtotal >= SAVE20_TRIGGER:
            discount = int(subtotal * SAVE20_DISCOUNT_RATE)
        else:
            discount = int(subtotal * SAVE20_SMALL_ORDER_RATE)
    elif coupon == "VIP":
        discount = VIP_DISCOUNT_LARGE
        if subtotal < VIP_TRIGGER:
            discount = VIP_DISCOUNT_SMALL
    else:
        raise ValueError("unknown coupon")
    
    return discount


def calculate_tax(amount):
    return int(amount * TAX_RATE)


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)
    
    currency = validate_request(user_id, items, currency)

    subtotal = calculate_subtotal(items)

    discount = calculate_discount(coupon, subtotal)

    total = subtotal - discount
    if total < 0:
        total = 0

    tax = calculate_tax(total)

    total += tax

    order_id = str(user_id) + "-" + str(len(items)) + "-" + "X"

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
