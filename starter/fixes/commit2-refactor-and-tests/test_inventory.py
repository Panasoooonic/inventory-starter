import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from inventory import Inventory, generate_order_id, process_order  # noqa: E402


def make_inventory():
    inv = Inventory()
    inv.add_item("pen", 2.0, 100)
    inv.add_item("laptop", 500.0, 5)
    return inv


def test_add_item_new_and_existing():
    inv = Inventory()
    inv.add_item("pen", 2.0, 10)
    inv.add_item("pen", 2.0, 5)
    assert inv.get_stock("pen") == 15


def test_get_stock_unknown_item():
    assert Inventory().get_stock("nothing") == 0


def test_remove_stock_success_and_failure():
    inv = make_inventory()
    assert inv.remove_stock("pen", 10) is True
    assert inv.get_stock("pen") == 90
    assert inv.remove_stock("pen", 1000) is False
    assert inv.remove_stock("ghost", 1) is False


def test_average_price():
    inv = make_inventory()
    assert inv.average_price() == 251.0


def test_generate_order_id_format():
    order_id = generate_order_id()
    assert order_id.startswith("ORD-")
    assert len(order_id) == 10


def test_process_order_regular_customer():
    inv = make_inventory()
    total = process_order(inv, [{"name": "pen", "qty": 10}], "regular", None, False, False)
    assert total == 20.0
    assert inv.get_stock("pen") == 90


def test_process_order_vip_discount_with_extras():
    inv = make_inventory()
    total = process_order(inv, [{"name": "laptop", "qty": 1}], "vip", None, True, True)
    # 500 * 0.8 = 400, + 15 express + 5 gift wrap
    assert total == 420.0


def test_process_order_unknown_item_fails():
    inv = make_inventory()
    assert process_order(inv, [{"name": "ghost", "qty": 1}], "regular", None, False, False) == -1


def test_process_order_empty_order_fails():
    assert process_order(make_inventory(), [], "regular", None, False, False) == -1


# ---- New tests added with the quality fixes ----
import pytest  # noqa: E402
from inventory import sales_report_text, stock_report_text  # noqa: E402


def test_average_price_empty_inventory_returns_zero():
    assert Inventory().average_price() == 0.0


def test_negative_quantity_rejected():
    with pytest.raises(ValueError):
        Inventory().add_item("pen", 2.0, -5)


def test_load_stock_missing_file_returns_false(tmp_path):
    assert Inventory().load_stock(str(tmp_path / "nope.json")) is False


def test_load_stock_valid_file(tmp_path):
    f = tmp_path / "stock.json"
    f.write_text('{"pen": {"price": 2.0, "qty": 7}}')
    inv = Inventory()
    assert inv.load_stock(str(f)) is True
    assert inv.get_stock("pen") == 7


@pytest.mark.parametrize("coupon,expected", [("SAVE10", 90.0), ("SAVE5", 95.0), (None, 100.0)])
def test_coupons(coupon, expected):
    inv = Inventory()
    inv.add_item("widget", 100.0, 5)
    assert process_order(inv, [{"name": "widget", "qty": 1}], "regular", coupon, False, False) == expected


def test_member_discount():
    inv = Inventory()
    inv.add_item("widget", 10.0, 5)
    assert process_order(inv, [{"name": "widget", "qty": 1}], "member", None, False, False) == 9.5


def test_reports():
    sales = [{"name": "pen", "qty": 2, "price": 3}]
    assert "TOTAL: 6" in sales_report_text(sales)
    assert "TOTAL: 20" in stock_report_text({"pen": {"qty": 10, "price": 2}})
