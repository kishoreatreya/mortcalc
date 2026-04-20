# mortcalc

A command-line mortgage calculator that produces a full amortization schedule with PMI and homeowners insurance support.

## Overview

Single-file Python CLI (`mortcalc.py`). No dependencies beyond the standard library.

## Usage

```bash
python3 mortcalc.py <principal> <rate> <term> [--pmi] [--pmi-rate RATE] [--insurance AMOUNT]
```

### Arguments

| Argument | Type | Description |
|---|---|---|
| `principal` | float | Total loan amount in dollars |
| `rate` | float | Annual interest rate as a percentage (e.g. `6.5`) |
| `term` | int | Mortgage term in years (e.g. `30`) |
| `--pmi` | flag | Enable PMI; drops off automatically when LTV reaches 80% |
| `--pmi-rate RATE` | float | Annual PMI rate as a percentage (default: `0.5`) |
| `--insurance AMOUNT` | float | Monthly homeowners insurance in dollars (optional, default: `0`) |

### Example

```bash
python3 mortcalc.py 300000 6.5 30 --pmi --pmi-rate 0.5 --insurance 150
```

## Output

- **Summary header**: loan amount, rate, term, PMI rate, insurance
- **Amortization table**: one row per month — total payment, principal paid, interest paid, PMI, insurance, remaining balance
- **Summary footer**: base P&I payment, PMI details (initial amount, month dropped, total paid), total interest, total loan cost

## Key Implementation Details

- **Amortization formula**: standard fixed-rate formula `P * [r(1+r)^n] / [(1+r)^n - 1]`
- **Zero-rate edge case**: divides principal evenly across months
- **PMI threshold**: 80% of the *original* principal (not appraised value); PMI is removed the month the balance first drops at or below that threshold
- **PMI amount**: calculated as `principal * (pmi_rate / 100) / 12` — based on original loan, not current balance

## Structure

```
mortcalc/
├── CLAUDE.md
└── mortcalc.py       # All logic: calculate_monthly_payment(), run(), main()
```
