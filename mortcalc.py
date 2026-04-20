#!/usr/bin/env python3
"""Mortgage calculator: computes monthly payment breakdown over the loan term."""

import argparse


def calculate_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    """Calculate fixed monthly P&I payment using the standard amortization formula."""
    if annual_rate == 0:
        return principal / term_months
    monthly_rate = annual_rate / 100 / 12
    return principal * (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)


def run(
    home_value: float,
    down_payment: float,
    annual_rate: float,
    term_years: int,
    pmi: bool,
    pmi_rate: float,
    homeowners_insurance: float,
) -> None:
    principal = home_value - down_payment
    down_pct = (down_payment / home_value) * 100
    term_months = term_years * 12
    pi_payment = calculate_monthly_payment(principal, annual_rate, term_months)

    # PMI applies until LTV drops to 80% of home value
    pmi_threshold = home_value * 0.80

    print(f"\nMortgage Summary")
    print(f"{'='*50}")
    print(f"  Home value:            ${home_value:>12,.2f}")
    print(f"  Down payment:          ${down_payment:>12,.2f} ({down_pct:.1f}%)")
    print(f"  Loan amount:           ${principal:>12,.2f}")
    print(f"  Interest rate:         {annual_rate:>11.3f}%")
    print(f"  Term:                  {term_years:>9} years ({term_months} months)")
    if pmi:
        print(f"  PMI rate:              {pmi_rate:>11.3f}% annually")
    if homeowners_insurance:
        print(f"  Homeowners insurance:  ${homeowners_insurance:>11,.2f}/mo")
    print(f"{'='*50}\n")

    balance = principal
    total_interest = 0.0
    total_pmi_paid = 0.0
    cumulative_payment = 0.0
    pmi_removed_month = None

    print(
        f"{'Mo':>4}  {'Mo Payment':>10}  {'Principal':>10}  {'Interest':>10}  "
        f"{'PMI':>8}  {'Ins':>8}  {'Cum Payment':>12}  {'Cum Interest':>13}  {'Balance':>12}"
    )
    print(
        f"{'-'*4}  {'-'*10}  {'-'*10}  {'-'*10}  "
        f"{'-'*8}  {'-'*8}  {'-'*12}  {'-'*13}  {'-'*12}"
    )

    for month in range(1, term_months + 1):
        monthly_rate = annual_rate / 100 / 12
        interest = balance * monthly_rate
        principal_paid = pi_payment - interest
        balance -= principal_paid
        if balance < 0:
            balance = 0

        total_interest += interest

        # PMI: charged while balance > 80% of home value
        pmi_this_month = 0.0
        if pmi and balance > pmi_threshold:
            pmi_this_month = principal * (pmi_rate / 100) / 12
            total_pmi_paid += pmi_this_month
        elif pmi and pmi_removed_month is None and balance <= pmi_threshold:
            pmi_removed_month = month

        monthly_payment = pi_payment + pmi_this_month + homeowners_insurance
        cumulative_payment += monthly_payment

        print(
            f"{month:>4}  ${monthly_payment:>9,.2f}  ${principal_paid:>9,.2f}  "
            f"${interest:>9,.2f}  ${pmi_this_month:>7,.2f}  ${homeowners_insurance:>7,.2f}  "
            f"${cumulative_payment:>11,.2f}  ${total_interest:>12,.2f}  ${balance:>11,.2f}"
        )

    initial_monthly_pmi = principal * (pmi_rate / 100) / 12 if pmi else 0.0
    initial_monthly_payment = pi_payment + initial_monthly_pmi + homeowners_insurance
    initial_annual_payment = initial_monthly_payment * 12
    total_cost = principal + total_interest + total_pmi_paid

    print(f"\n{'='*50}")
    print(f"  Base monthly P&I:      ${pi_payment:>11,.2f}")
    if pmi:
        print(f"  Initial monthly PMI:   ${initial_monthly_pmi:>11,.2f}")
        if pmi_removed_month:
            print(f"  PMI removed after:     month {pmi_removed_month}")
        print(f"  Total PMI paid:        ${total_pmi_paid:>11,.2f}")
    if homeowners_insurance:
        print(f"  Monthly insurance:     ${homeowners_insurance:>11,.2f}")
    print(f"  Monthly payment:       ${initial_monthly_payment:>11,.2f}")
    print(f"  Annual payment:        ${initial_annual_payment:>11,.2f}")
    print(f"  Total interest paid:   ${total_interest:>11,.2f}")
    print(f"  Total payment:         ${cumulative_payment:>11,.2f}")
    print(f"  Total cost of loan:    ${total_cost:>11,.2f}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate monthly mortgage payments over the loan term.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("home_value", type=float, help="Total home value in dollars")
    parser.add_argument("down_payment", type=float, help="Down payment amount in dollars")
    parser.add_argument("rate", type=float, help="Annual interest rate as a percentage (e.g. 6.5)")
    parser.add_argument("term", type=int, help="Mortgage term in years (e.g. 30)")
    parser.add_argument(
        "--pmi",
        action="store_true",
        default=False,
        help="Include PMI (charged until LTV reaches 80%%)",
    )
    parser.add_argument(
        "--pmi-rate",
        type=float,
        default=0.5,
        metavar="RATE",
        help="Annual PMI rate as a percentage (e.g. 0.5)",
    )
    parser.add_argument(
        "--insurance",
        type=float,
        default=0.0,
        metavar="AMOUNT",
        help="Monthly homeowners insurance amount in dollars",
    )

    args = parser.parse_args()

    if args.down_payment >= args.home_value:
        parser.error("down_payment must be less than home_value")
    if args.pmi and args.pmi_rate <= 0:
        parser.error("--pmi-rate must be positive when --pmi is set")

    run(
        home_value=args.home_value,
        down_payment=args.down_payment,
        annual_rate=args.rate,
        term_years=args.term,
        pmi=args.pmi,
        pmi_rate=args.pmi_rate,
        homeowners_insurance=args.insurance,
    )


if __name__ == "__main__":
    main()
