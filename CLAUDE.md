# mortcalc

A command-line mortgage calculator that produces a full amortization schedule with PMI and homeowners insurance support, with optional HTML report output.

## Overview

Single-file Python CLI (`mortcalc.py`). No dependencies beyond the standard library (HTML output loads Chart.js from CDN).

## Usage

```bash
python3 mortcalc.py <home_value> <down_payment> <rate> <term> [options]
```

### Arguments

| Argument | Type | Description |
|---|---|---|
| `home_value` | float | Total home value in dollars |
| `down_payment` | float | Down payment amount in dollars |
| `rate` | float | Annual interest rate as a percentage (e.g. `6.5`) |
| `term` | int | Mortgage term in years (e.g. `30`) |
| `--pmi` | flag | Enable PMI; drops off automatically when LTV reaches 80% of home value |
| `--pmi-rate RATE` | float | Annual PMI rate as a percentage (default: `0.5`) |
| `--insurance AMOUNT` | float | Monthly homeowners insurance in dollars (default: `0`) |
| `--html` | flag | Generate an HTML report with charts |
| `--html-output FILE` | str | Output filename for the HTML report (default: `mortgage.html`) |

### Examples

```bash
# Terminal output only
python3 mortcalc.py 2000000 250000 6.5 30 --pmi --pmi-rate 0.5 --insurance 200

# Also generate HTML report
python3 mortcalc.py 2000000 250000 6.5 30 --pmi --pmi-rate 0.5 --insurance 200 --html

# Custom HTML output filename
python3 mortcalc.py 2000000 250000 6.5 30 --html --html-output report.html
```

## Output

### Terminal
- **Summary header**: home value, down payment, loan amount, rate, term, PMI rate, insurance
- **Amortization table**: one row per month — monthly payment, principal, interest, PMI, insurance, cumulative payment, cumulative interest, remaining balance
- **Summary footer**: base P&I, PMI details, monthly payment, annual payment, total interest, total payment, total cost of loan

### HTML Report (`--html`)
Self-contained HTML file with four Chart.js charts and a styled amortization table:
1. **Remaining Balance Over Time** — line chart of loan paydown
2. **Monthly Principal vs Interest vs PMI** — line chart showing payment composition shift
3. **Cumulative Payment vs Cumulative Interest** — total cash out vs interest portion
4. **Monthly Payment Breakdown (Stacked Bar)** — principal, interest, PMI, and insurance per month

## Key Implementation Details

- **Amortization formula**: standard fixed-rate formula `P * [r(1+r)^n] / [(1+r)^n - 1]`
- **Zero-rate edge case**: divides principal evenly across months
- **PMI threshold**: 80% of *home value* (not loan amount); PMI is removed the month the balance first drops at or below that threshold
- **PMI amount**: calculated as `principal * (pmi_rate / 100) / 12` — based on original loan, not current balance
- **Loan amount**: derived as `home_value - down_payment`

## Code Structure

```
mortcalc/
├── CLAUDE.md
└── mortcalc.py
    ├── calculate_monthly_payment()  # amortization formula
    ├── amortize()                   # runs schedule, returns data dict with all rows
    ├── print_text()                 # renders terminal output from data dict
    ├── generate_html()              # renders HTML report from data dict
    └── run() / main()               # orchestration and argument parsing
```
