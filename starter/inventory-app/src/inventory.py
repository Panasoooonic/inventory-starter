"""Inventory and order processing module for a small shop.

This is the BASELINE version. It works, but it contains realistic
code-quality weaknesses that static analysis tends to flag.
"""
import os
import sys
import json
import random


class Inventory:
    def __init__(self):
        self.items = {}

    def add_item(self, name, price, qty):
        """Add a new item or increase the stock of an existing one."""
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
        total = 0
        for name in self.items:
            total += self.items[name]["price"]
        return total / len(self.items)

    def load_stock(self, path):
        """Load stock from a JSON file. Returns True on success."""
        try:
            with open(path) as handle:
                data = json.load(handle)
            for name, info in data.items():
                self.add_item(name, info["price"], info["qty"])
            return True
        except:
            return False


def generate_order_id():
    return "ORD-" + str(random.randint(100000, 999999))


def process_order(inventory, order, customer_type, coupon, express, gift_wrap):
    """Process an order and return the final total, or -1 on failure."""
    temp_note = "processing"
    total = 0
    if order:
        for line in order:
            name = line["name"]
            qty = line["qty"]
            if name in inventory.items:
                if inventory.items[name]["qty"] >= qty:
                    price = inventory.items[name]["price"]
                    line_total = price * qty
                    if customer_type == "vip":
                        if line_total > 100:
                            line_total = line_total * 0.8
                        else:
                            line_total = line_total * 0.9
                    elif customer_type == "member":
                        if line_total > 100:
                            line_total = line_total * 0.9
                        else:
                            line_total = line_total * 0.95
                    if coupon == "SAVE10":
                        if line_total > 50:
                            line_total = line_total - 10
                    elif coupon == "SAVE5":
                        if line_total > 20:
                            line_total = line_total - 5
                    total += line_total
                    inventory.remove_stock(name, qty)
                else:
                    return -1
            else:
                return -1
        if express:
            total += 15
        if gift_wrap:
            total += 5
        return round(total, 2)
    return -1


def sales_report_text(sales):
    lines = []
    lines.append("SALES REPORT")
    lines.append("=" * 20)
    grand_total = 0
    for sale in sales:
        lines.append(sale["name"] + ": " + str(sale["qty"]) + " units")
        lines.append("  revenue: " + str(sale["qty"] * sale["price"]))
        grand_total += sale["qty"] * sale["price"]
    lines.append("-" * 20)
    lines.append("TOTAL: " + str(grand_total))
    return "\n".join(lines)


def stock_report_text(items):
    lines = []
    lines.append("STOCK REPORT")
    lines.append("=" * 20)
    grand_total = 0
    for name in items:
        lines.append(name + ": " + str(items[name]["qty"]) + " units")
        lines.append("  value: " + str(items[name]["qty"] * items[name]["price"]))
        grand_total += items[name]["qty"] * items[name]["price"]
    lines.append("-" * 20)
    lines.append("TOTAL: " + str(grand_total))
    return "\n".join(lines)
