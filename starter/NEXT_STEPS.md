# Your exact steps (VS Code + Git + SonarQube Cloud)

Project: **Inventory & Order Processing** (Python 3.12, pytest 8.3.4, pytest-cov 6.0.0)

Folder layout of this ZIP:

```
inventory-app/     <- YOUR REPO. This is the untouched BASELINE code.
ci-files/          <- Added in commit 2 (NOT in the baseline commit)
fixes/             <- Ready-made fixed files for Part D (copy in later)
```

---

## 1. Create the repo with the untouched baseline (Part A1)

1. Unzip. In VS Code: **File > Open Folder > `inventory-app`**.
2. Open the terminal (Ctrl+`) and run:

```bash
git init
git branch -M main
git add .
git commit -m "Baseline: original application code (v1.0.0)"
git tag baseline-v1.0.0
```

3. **Source Control sidebar > Publish Branch** (choose a public repo). Then:

```bash
git push origin baseline-v1.0.0
```

Record the baseline commit hash with `git log --oneline` (you cite it in the report).

> Do not copy `ci-files/` or `fixes/` into the repo yet.

## 2. SonarQube Cloud setup (Part A2, A3)

1. Go to sonarcloud.io > **Log in with GitHub** > create/select your organization.
2. **Analyze new project** > pick your repo > choose **With GitHub Actions**.
3. **Project > Administration > Analysis Method** > turn **Automatic Analysis OFF**.
4. Copy the exact **Project Key** and **Organization Key** (Project > Information).
5. **My Account > Security > Generate Token**, copy it once.
6. GitHub repo > **Settings > Secrets and variables > Actions > New repository secret**:
   name `SONAR_TOKEN`, value = your token. Never paste it anywhere else.

## 3. Add CI files (Part B), baseline scan

1. Copy the contents of `ci-files/` into the repo root (keep the `.github/workflows/` folders).
2. Open `sonar-project.properties` and replace the two `REPLACE_WITH...` values with your exact keys.
3. Commit and push:

```bash
git add .github sonar-project.properties
git commit -m "Add SonarQube Cloud CI workflow (no code changes)"
git push
```

4. GitHub **Actions** tab: open the run, confirm: tests pass (9 passed), `coverage.xml` generated, scan says analysis successful. Screenshot + save the run URL.
5. SonarQube Cloud dashboard: record analysis date, commit hash, issue totals by category and severity, coverage, duplication, quality gate status (both **New Code** and **Overall Code**). Screenshot as `baseline_dashboard.png`.

Expected baseline (your numbers may differ slightly, always report what the dashboard actually shows): coverage about 60%, several maintainability issues, possibly a security hotspot for `random`.

## 3b. Likely findings to choose from (Part C)

| Likely finding | File / area | Category |
|---|---|---|
| Cognitive Complexity too high (S3776) | `process_order` | Maintainability |
| Unused imports (S1128) / unused local variable `temp_note` (S1481) | top of `inventory.py`, `process_order` | Maintainability |
| Bare `except` (S5754) | `Inventory.load_stock` | Reliability / Maintainability |
| Too many parameters (S107) | `process_order` | Maintainability |
| Duplicated blocks | `sales_report_text` / `stock_report_text` | Maintainability |
| Pseudorandom generator hotspot (S2245) | `generate_order_id` | Security hotspot |

Always record the **real line numbers and wording from your own dashboard**. Find the actual findings by opening **Issues**; don't copy this table into the report.

**Independently tested risks** (found by tests, not by the scanner):
- `average_price()` on an empty inventory raises `ZeroDivisionError`.
- `add_item("pen", 2.0, -5)` silently accepts negative stock.

Prove them with a test BEFORE fixing (run this, show it failing, screenshot it):

```python
import pytest
def test_average_price_empty_inventory_returns_zero():
    assert Inventory().average_price() == 0.0      # fails at baseline: ZeroDivisionError

def test_negative_quantity_rejected():
    with pytest.raises(ValueError):
        Inventory().add_item("pen", 2.0, -5)       # fails at baseline: no error raised
```

## 4. Fix and re-analyze (Part D)

Use **separate commits** so each fix is traceable. The baseline commit stays untouched.

**Commit 3: fix unused imports + bare except**

```bash
copy ..\fixes\commit1-unused-imports-and-bare-except\inventory.py src\inventory.py   # Mac/Linux: cp
git add src/inventory.py
git commit -m "Fix S1128 unused imports and S5754 bare except in load_stock"
```

**Commit 4: refactor complexity, remove duplication, add validation and tests**

```bash
copy ..\fixes\commit2-refactor-and-tests\inventory.py src\inventory.py
copy ..\fixes\commit2-refactor-and-tests\test_inventory.py tests\test_inventory.py
git add src tests
git commit -m "Refactor process_order (S3776), dedupe reports, validate input, add tests"
```

Locally: `pytest --cov=src --cov-report=xml:coverage.xml` (expect 18 passed, about 100% coverage).

Then `git push`. Confirm the **new** Actions run reran tests and regenerated `coverage.xml`, scanned with the SAME project key, and screenshot the final dashboard as `final_dashboard.png`. Do not reuse baseline screenshots.

Tip: If you prefer to do the refactor yourself, use the fixes only as reference. You will understand the report better.

## 5. Evidence and report (Part D12 and report)

```bash
git log --oneline
git diff baseline-v1.0.0 HEAD --stat
```

Comparison table to fill in from your dashboards (baseline vs final): total issues, issues by category, coverage (overall and new code), duplication, quality gate.

Explain **new code vs overall code**: the Sonar quality gate judges new code only, so the final gate can pass even if older issues remain. Also report anything that did NOT improve.

Reflection ideas:
- Static-analysis limits: it can't tell whether discount rules match business requirements, and 100% line coverage doesn't prove the assertions are meaningful.
- Independently tested risk: the empty-inventory `ZeroDivisionError` and negative stock above.
- Troubleshooting: describe a real problem you hit (Automatic Analysis conflict, wrong project key, coverage not found, YAML indentation, failed tests blocking the scan) and how you fixed it. If you hit none, say so honestly rather than inventing one.

## Honest-reporting reminders
- Report the numbers the dashboards actually show.
- Never commit `.env`, tokens, or your `.venv` folder.
- Replace placeholder name/ID/URLs in the report with your own.
