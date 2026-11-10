"""Inventory and order processing module for a small shop.

This is the BASELINE version. It works, but it contains realistic
code-quality weaknesses that static analysis tends to flag.
"""
import json
import random


class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, name, price, qty):
        """Add a new item or increase the stock of an existing one."""
        if qty < 0 or price < 0:
            raise ValueError("price and qty must not be negative")
        if name in self.items:
            self.items[name]["qty"] += qty
        else:
            self.items[name] = {"price": price, "qty": qty}

    def get_stock(self, name):
        if name in self.items:
            return self.items[name]["qty"]
        return 0

    def remove_stock(self, name, qty):
        if name not in self.items:
            return False
        if self.items[name]["qty"] < qty:
            return False
        self.items[name]["qty"] -= qty
        return True

    def average_price(self):
        """Average unit price across all item types."""
        if not self.items:
            return 0.0
        return sum(info["price"] for info in self.items.values()) / len(self.items)

    def load_stock(self, path):
        """Load stock from a JSON file. Returns True on success."""
        try:
            with open(path) as handle:
                data = json.load(handle)
            for name, info in data.items():
                self.add_item(name, info["price"], info["qty"])
            return True
        except (OSError, ValueError, KeyError):
            return False


def generate_order_id():
    return "ORD-" + str(random.randint(100000, 999999))


DISCOUNTS = {
    "vip": (0.8, 0.9),
    "member": (0.9, 0.95),
}


def _apply_customer_discount(line_total, customer_type):
    if customer_type not in DISCOUNTS:
        return line_total
    big_rate, small_rate = DISCOUNTS[customer_type]
    return line_total * (big_rate if line_total > 100 else small_rate)


def _apply_coupon(line_total, coupon):
    if coupon == "SAVE10" and line_total > 50:
        return line_total - 10
    if coupon == "SAVE5" and line_total > 20:
        return line_total - 5
    return line_total


def process_order(inventory, order, customer_type, coupon, express, gift_wrap):
    """Process an order and return the final total, or -1 on failure."""
    if not order:
        return -1
    total = 0
    for line in order:
        name, qty = line["name"], line["qty"]
        if inventory.get_stock(name) < qty or name not in inventory.items:
            return -1
        line_total = inventory.items[name]["price"] * qty
        line_total = _apply_customer_discount(line_total, customer_type)
        line_total = _apply_coupon(line_total, coupon)
        total += line_total
        inventory.remove_stock(name, qty)
    if express:
        total += 15
    if gift_wrap:
        total += 5
    return round(total, 2)


def _build_report(title, rows, label):
    """rows: iterable of (name, qty, unit_price)."""
    lines = [title, "=" * 20]
    grand_total = 0
    for name, qty, unit_price in rows:
        value = qty * unit_price
        lines.append(f"{name}: {qty} units")
        lines.append(f"  {label}: {value}")
        grand_total += value
    lines.append("-" * 20)
    lines.append(f"TOTAL: {grand_total}")
    return "\n".join(lines)


def sales_report_text(sales):
    rows = [(s["name"], s["qty"], s["price"]) for s in sales]
    return _build_report("SALES REPORT", rows, "revenue")


def stock_report_text(items):
    rows = [(name, info["qty"], info["price"]) for name, info in items.items()]
    return _build_report("STOCK REPORT", rows, "value")
