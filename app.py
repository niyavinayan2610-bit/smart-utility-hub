from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from uuid import uuid4

from flask import Flask, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024

# Linear conversion factors are expressed in meters or kilograms.
UNITS = {
    "length": {
        "m": ("Meters", "1"), "km": ("Kilometers", "1000"),
        "cm": ("Centimeters", ".01"), "mm": ("Millimeters", ".001"),
        "mi": ("Miles", "1609.344"), "yd": ("Yards", ".9144"),
        "ft": ("Feet", ".3048"), "in": ("Inches", ".0254"),
    },
    "weight": {
        "kg": ("Kilograms", "1"), "g": ("Grams", ".001"),
        "mg": ("Milligrams", ".000001"), "lb": ("Pounds", ".45359237"),
        "oz": ("Ounces", ".028349523125"),
    },
    "temperature": {
        "°C": ("Celsius", None), "°F": ("Fahrenheit", None),
        "K": ("Kelvin", None),
    },
}
TIERS = [(10000, 15), (5000, 10), (1000, 5), (0, 0)]
CURRENCY = "₹"
MAX_ITEMS = 50
CENT = Decimal("0.01")


def read_number(raw, label, limit):
    try:
        value = Decimal(raw.strip()) if len(raw) <= 64 else Decimal("NaN")
    except InvalidOperation:
        raise ValueError(f"{label} must be a valid number.") from None
    if not value.is_finite():
        raise ValueError(f"{label} must be a valid number.")
    if value.copy_abs() > limit or (value and value.copy_abs() < Decimal("1e-30")):
        raise ValueError(f"{label} is outside the supported range.")
    return value


def convert(value, category, source, target):
    units = UNITS.get(category, {})
    if source not in units or target not in units:
        raise ValueError("Choose two units from the selected category.")

    if category != "temperature":
        if value < 0:
            raise ValueError("Length and weight cannot be negative.")
        if source == target:
            return value
        return value * Decimal(units[source][1]) / Decimal(units[target][1])

    if source == "°F":
        celsius = (value - 32) * 5 / 9
    elif source == "K":
        celsius = value - Decimal("273.15")
    else:
        celsius = value

    if celsius < Decimal("-273.15"):
        raise ValueError("Temperature cannot be below absolute zero.")
    if source == target:
        return value
    if target == "°F":
        return celsius * 9 / 5 + 32
    if target == "K":
        return celsius + Decimal("273.15")
    return celsius


def display_number(value):
    if not value:
        return "0"
    rounded = Decimal(f"{value:.12g}").normalize()
    if -6 <= rounded.adjusted() < 12:
        return format(rounded, "f")
    return format(rounded, "e")


@app.route("/", methods=["GET", "POST"])
def converter():
    category = request.form.get("category", "length")
    source = request.form.get("source", "m")
    target = request.form.get("target", "ft")
    raw = request.form.get("value", "")
    result = None
    error = None
    if request.method == "POST":
        try:
            value = read_number(raw, "Measurement", 10**15)
            converted = convert(value, category, source, target)
            result = {"input": display_number(value), "output": display_number(converted)}
        except ValueError as exc:
            error = str(exc)
    if category not in UNITS:
        category = "length"
    options = list(UNITS[category])
    if source not in options:
        source = options[0]
    if target not in options:
        target = options[1]
    return render_template(
        "converter.html", active="converter", units=UNITS, category=category,
        source=source, target=target, raw=raw, result=result, error=error,
    ), 400 if error else 200


def field(value, label, length, required=False):
    value = value.strip()
    if required and not value:
        raise ValueError(f"Enter {label}.")
    if len(value) > length:
        raise ValueError(f"{label.capitalize()} must be at most {length} characters.")
    return value


def make_invoice(customer, rows):
    customer = {
        "name": field(customer["name"], "customer name", 100, required=True),
        "contact": field(customer["contact"], "contact details", 150),
        "address": field(customer["address"], "address", 250),
    }
    items = []
    for index, row in enumerate(rows, 1):
        name = field(row["product"], f"a product name for item {index}", 100, required=True)
        quantity = read_number(row["quantity"], f"Item {index} quantity", 1000000)
        if quantity < 1 or quantity != quantity.to_integral_value():
            raise ValueError(f"Item {index} quantity must be a positive whole number.")
        price = read_number(row["price"], f"Item {index} unit price", 100000000)
        if price < 0 or price != price.quantize(CENT):
            raise ValueError(f"Item {index} unit price must be nonnegative with at most two decimal places.")
        items.append({"name": name, "quantity": int(quantity), "price": price, "amount": price * quantity})

    subtotal = sum(item["amount"] for item in items)
    rate = next(rate for minimum, rate in TIERS if subtotal >= minimum)
    discount = (subtotal * rate / 100).quantize(CENT, rounding=ROUND_HALF_UP)
    return {
        "number": uuid4().hex[:12].upper(), "date": date.today().strftime("%d %b %Y"),
        "customer": customer, "items": items, "subtotal": subtotal, "rate": rate,
        "discount": discount, "total": subtotal - discount,
    }


@app.route("/billing", methods=["GET", "POST"])
def billing():
    customer = {key: request.form.get(key, "") for key in ("name", "contact", "address")}
    keys = ("product", "quantity", "price")
    rows = [{"product": "", "quantity": "1", "price": ""}]
    invoice = None
    error = None
    if request.method == "POST":
        columns = [request.form.getlist(key) for key in keys]
        if len({len(column) for column in columns}) != 1 or not 1 <= len(columns[0]) <= MAX_ITEMS:
            error = f"Submit between 1 and {MAX_ITEMS} complete item rows."
        else:
            rows = [dict(zip(keys, values)) for values in zip(*columns)]
            try:
                invoice = make_invoice(customer, rows)
            except ValueError as exc:
                error = str(exc)
    return render_template(
        "billing.html", active="billing", customer=customer, rows=rows, tiers=TIERS,
        currency=CURRENCY, invoice=invoice, error=error, max_items=MAX_ITEMS,
    ), 400 if error else 200


if __name__ == "__main__":
    app.run()
