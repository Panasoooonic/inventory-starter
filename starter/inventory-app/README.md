# Inventory & Order Processing

A small Python 3.12 module that manages shop inventory and processes customer
orders (discounts by customer type, coupons, express shipping, gift wrap) and
produces simple text reports.

- **Language:** Python 3.12
- **Test framework:** pytest 8.3.4 with pytest-cov 6.0.0
- **Baseline version:** v1.0.0 (original code, before any quality improvements)

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest --cov=src --cov-report=xml:coverage.xml --cov-report=term
```
