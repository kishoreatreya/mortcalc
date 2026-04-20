#!/usr/bin/env python3
"""Mortgage calculator: computes monthly payment breakdown over the loan term."""

import argparse
import json


def calculate_monthly_payment(principal: float, annual_rate: float, term_months: int) -> float:
    """Calculate fixed monthly P&I payment using the standard amortization formula."""
    if annual_rate == 0:
        return principal / term_months
    monthly_rate = annual_rate / 100 / 12
    return principal * (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)


def amortize(
    home_value: float,
    down_payment: float,
    annual_rate: float,
    term_years: int,
    pmi: bool,
    pmi_rate: float,
    homeowners_insurance: float,
) -> dict:
    """Run the amortization schedule and return all computed data."""
    principal = home_value - down_payment
    term_months = term_years * 12
    pi_payment = calculate_monthly_payment(principal, annual_rate, term_months)
    pmi_threshold = home_value * 0.80
    initial_monthly_pmi = principal * (pmi_rate / 100) / 12 if pmi else 0.0

    rows = []
    balance = principal
    total_interest = 0.0
    total_pmi_paid = 0.0
    cumulative_payment = 0.0
    pmi_removed_month = None

    for month in range(1, term_months + 1):
        monthly_rate = annual_rate / 100 / 12
        interest = balance * monthly_rate
        principal_paid = pi_payment - interest
        balance -= principal_paid
        if balance < 0:
            balance = 0

        total_interest += interest

        pmi_this_month = 0.0
        if pmi and balance > pmi_threshold:
            pmi_this_month = principal * (pmi_rate / 100) / 12
            total_pmi_paid += pmi_this_month
        elif pmi and pmi_removed_month is None and balance <= pmi_threshold:
            pmi_removed_month = month

        monthly_payment = pi_payment + pmi_this_month + homeowners_insurance
        cumulative_payment += monthly_payment

        rows.append({
            "month": month,
            "monthly_payment": monthly_payment,
            "principal_paid": principal_paid,
            "interest": interest,
            "pmi": pmi_this_month,
            "insurance": homeowners_insurance,
            "cumulative_payment": cumulative_payment,
            "cumulative_interest": total_interest,
            "balance": balance,
        })

    initial_monthly_payment = pi_payment + initial_monthly_pmi + homeowners_insurance

    return {
        "home_value": home_value,
        "down_payment": down_payment,
        "down_pct": (down_payment / home_value) * 100,
        "principal": principal,
        "annual_rate": annual_rate,
        "term_years": term_years,
        "term_months": term_months,
        "pmi": pmi,
        "pmi_rate": pmi_rate,
        "homeowners_insurance": homeowners_insurance,
        "pi_payment": pi_payment,
        "initial_monthly_pmi": initial_monthly_pmi,
        "initial_monthly_payment": initial_monthly_payment,
        "initial_annual_payment": initial_monthly_payment * 12,
        "pmi_removed_month": pmi_removed_month,
        "total_pmi_paid": total_pmi_paid,
        "total_interest": total_interest,
        "cumulative_payment": cumulative_payment,
        "total_cost": principal + total_interest + total_pmi_paid,
        "rows": rows,
    }


def print_text(data: dict, show_table: bool = True) -> None:
    d = data
    print(f"\nMortgage Summary")
    print(f"{'='*50}")
    print(f"  Home value:            ${d['home_value']:>12,.2f}")
    print(f"  Down payment:          ${d['down_payment']:>12,.2f} ({d['down_pct']:.1f}%)")
    print(f"  Loan amount:           ${d['principal']:>12,.2f}")
    print(f"  Interest rate:         {d['annual_rate']:>11.3f}%")
    print(f"  Term:                  {d['term_years']:>9} years ({d['term_months']} months)")
    if d["pmi"]:
        print(f"  PMI rate:              {d['pmi_rate']:>11.3f}% annually")
    if d["homeowners_insurance"]:
        print(f"  Homeowners insurance:  ${d['homeowners_insurance']:>11,.2f}/mo")
    print(f"{'='*50}\n")

    if show_table:
        print(
            f"{'Mo':>4}  {'Mo Payment':>10}  {'Principal':>10}  {'Interest':>10}  "
            f"{'PMI':>8}  {'Ins':>8}  {'Cum Payment':>12}  {'Cum Interest':>13}  {'Balance':>12}"
        )
        print(
            f"{'-'*4}  {'-'*10}  {'-'*10}  {'-'*10}  "
            f"{'-'*8}  {'-'*8}  {'-'*12}  {'-'*13}  {'-'*12}"
        )

    if show_table:
        for r in d["rows"]:
            print(
                f"{r['month']:>4}  ${r['monthly_payment']:>9,.2f}  ${r['principal_paid']:>9,.2f}  "
                f"${r['interest']:>9,.2f}  ${r['pmi']:>7,.2f}  ${r['insurance']:>7,.2f}  "
                f"${r['cumulative_payment']:>11,.2f}  ${r['cumulative_interest']:>12,.2f}  ${r['balance']:>11,.2f}"
            )

    print(f"\n{'='*50}")
    print(f"  Base monthly P&I:      ${d['pi_payment']:>11,.2f}")
    if d["pmi"]:
        print(f"  Initial monthly PMI:   ${d['initial_monthly_pmi']:>11,.2f}")
        if d["pmi_removed_month"]:
            print(f"  PMI removed after:     month {d['pmi_removed_month']}")
        print(f"  Total PMI paid:        ${d['total_pmi_paid']:>11,.2f}")
    if d["homeowners_insurance"]:
        print(f"  Monthly insurance:     ${d['homeowners_insurance']:>11,.2f}")
    print(f"  Monthly payment:       ${d['initial_monthly_payment']:>11,.2f}")
    print(f"  Annual payment:        ${d['initial_annual_payment']:>11,.2f}")
    print(f"  Total interest paid:   ${d['total_interest']:>11,.2f}")
    print(f"  Total payment:         ${d['cumulative_payment']:>11,.2f}")
    print(f"  Total cost of loan:    ${d['total_cost']:>11,.2f}")
    print(f"{'='*50}\n")


def generate_html(data: dict, output_path: str) -> None:
    d = data
    rows = d["rows"]

    labels = json.dumps([r["month"] for r in rows])
    balance_data = json.dumps([round(r["balance"], 2) for r in rows])
    principal_data = json.dumps([round(r["principal_paid"], 2) for r in rows])
    interest_data = json.dumps([round(r["interest"], 2) for r in rows])
    pmi_data = json.dumps([round(r["pmi"], 2) for r in rows])
    cum_payment_data = json.dumps([round(r["cumulative_payment"], 2) for r in rows])
    cum_interest_data = json.dumps([round(r["cumulative_interest"], 2) for r in rows])

    pmi_badge = (
        f'<span class="badge">PMI removed month {d["pmi_removed_month"]}</span>'
        if d["pmi"] and d["pmi_removed_month"] else ""
    )

    summary_rows = [
        ("Home Value", f'${d["home_value"]:,.2f}'),
        ("Down Payment", f'${d["down_payment"]:,.2f} ({d["down_pct"]:.1f}%)'),
        ("Loan Amount", f'${d["principal"]:,.2f}'),
        ("Interest Rate", f'{d["annual_rate"]:.3f}%'),
        ("Term", f'{d["term_years"]} years ({d["term_months"]} months)'),
    ]
    if d["pmi"]:
        summary_rows.append(("PMI Rate", f'{d["pmi_rate"]:.3f}% annually'))
    if d["homeowners_insurance"]:
        summary_rows.append(("Homeowners Insurance", f'${d["homeowners_insurance"]:,.2f}/mo'))
    summary_rows += [
        ("Base Monthly P&amp;I", f'${d["pi_payment"]:,.2f}'),
    ]
    if d["pmi"]:
        summary_rows.append(("Initial Monthly PMI", f'${d["initial_monthly_pmi"]:,.2f}'))
        summary_rows.append(("Total PMI Paid", f'${d["total_pmi_paid"]:,.2f}'))
    summary_rows += [
        ("Monthly Payment", f'${d["initial_monthly_payment"]:,.2f}'),
        ("Annual Payment", f'${d["initial_annual_payment"]:,.2f}'),
        ("Total Interest Paid", f'${d["total_interest"]:,.2f}'),
        ("Total Payment", f'${d["cumulative_payment"]:,.2f}'),
        ("Total Cost of Loan", f'${d["total_cost"]:,.2f}'),
    ]

    summary_html = "\n".join(
        f"<tr><td>{label}</td><td>{value}</td></tr>" for label, value in summary_rows
    )

    table_rows_html = ""
    for r in rows:
        table_rows_html += (
            f"<tr>"
            f"<td>{r['month']}</td>"
            f"<td>${r['monthly_payment']:,.2f}</td>"
            f"<td>${r['principal_paid']:,.2f}</td>"
            f"<td>${r['interest']:,.2f}</td>"
            f"<td>${r['pmi']:,.2f}</td>"
            f"<td>${r['insurance']:,.2f}</td>"
            f"<td>${r['cumulative_payment']:,.2f}</td>"
            f"<td>${r['cumulative_interest']:,.2f}</td>"
            f"<td>${r['balance']:,.2f}</td>"
            f"</tr>\n"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mortgage Calculator</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{ font-family: system-ui, sans-serif; background: #f4f6f9; color: #222; margin: 0; padding: 24px; }}
    h1 {{ font-size: 1.6rem; margin-bottom: 4px; }}
    h2 {{ font-size: 1.1rem; color: #444; margin: 32px 0 12px; }}
    .badge {{ background: #e8f4e8; color: #2a7a2a; border-radius: 4px; padding: 2px 10px; font-size: 0.8rem; margin-left: 8px; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; margin-bottom: 32px; }}
    .summary-grid table {{ background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.08); width: 100%; border-collapse: collapse; }}
    .summary-grid td {{ padding: 8px 14px; border-bottom: 1px solid #f0f0f0; font-size: 0.9rem; }}
    .summary-grid td:first-child {{ color: #666; }}
    .summary-grid td:last-child {{ font-weight: 600; text-align: right; }}
    .charts {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(480px, 1fr)); gap: 24px; margin-bottom: 36px; }}
    .chart-box {{ background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.08); padding: 20px; }}
    .chart-box canvas {{ max-height: 300px; }}
    .table-wrap {{ overflow-x: auto; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
    table.amort {{ border-collapse: collapse; width: 100%; font-size: 0.82rem; }}
    table.amort th {{ background: #2c3e50; color: #fff; padding: 10px 12px; text-align: right; white-space: nowrap; }}
    table.amort th:first-child {{ text-align: center; }}
    table.amort td {{ padding: 6px 12px; text-align: right; border-bottom: 1px solid #f0f0f0; }}
    table.amort td:first-child {{ text-align: center; font-weight: 600; }}
    table.amort tr:hover td {{ background: #f7f9fc; }}
    table.amort tr.pmi-drop td {{ background: #fffbe6; }}
  </style>
</head>
<body>
  <h1>Mortgage Amortization Report {pmi_badge}</h1>

  <h2>Loan Summary</h2>
  <div class="summary-grid">
    <table>{summary_html}</table>
  </div>

  <h2>Charts</h2>
  <div class="charts">
    <div class="chart-box">
      <canvas id="balanceChart"></canvas>
    </div>
    <div class="chart-box">
      <canvas id="breakdownChart"></canvas>
    </div>
    <div class="chart-box">
      <canvas id="cumulativeChart"></canvas>
    </div>
    <div class="chart-box">
      <canvas id="monthlyBreakdownChart"></canvas>
    </div>
  </div>

  <h2>Amortization Schedule</h2>
  <div class="table-wrap">
    <table class="amort">
      <thead>
        <tr>
          <th>Mo</th><th>Mo Payment</th><th>Principal</th><th>Interest</th>
          <th>PMI</th><th>Insurance</th><th>Cum Payment</th><th>Cum Interest</th><th>Balance</th>
        </tr>
      </thead>
      <tbody>
        {table_rows_html}
      </tbody>
    </table>
  </div>

  <script>
    const labels = {labels};
    const fmt = (v) => '$' + v.toLocaleString('en-US', {{minimumFractionDigits: 2, maximumFractionDigits: 2}});

    // 1. Remaining Balance
    new Chart(document.getElementById('balanceChart'), {{
      type: 'line',
      data: {{
        labels,
        datasets: [{{
          label: 'Remaining Balance',
          data: {balance_data},
          borderColor: '#2c7be5',
          backgroundColor: 'rgba(44,123,229,0.08)',
          fill: true,
          pointRadius: 0,
          tension: 0.3,
        }}]
      }},
      options: {{
        plugins: {{ title: {{ display: true, text: 'Remaining Balance Over Time' }} }},
        scales: {{ y: {{ ticks: {{ callback: fmt }} }} }},
      }}
    }});

    // 2. Monthly Principal vs Interest
    new Chart(document.getElementById('breakdownChart'), {{
      type: 'line',
      data: {{
        labels,
        datasets: [
          {{ label: 'Principal', data: {principal_data}, borderColor: '#27ae60', backgroundColor: 'rgba(39,174,96,0.08)', fill: true, pointRadius: 0, tension: 0.3 }},
          {{ label: 'Interest',  data: {interest_data},  borderColor: '#e74c3c', backgroundColor: 'rgba(231,76,60,0.08)',  fill: true, pointRadius: 0, tension: 0.3 }},
          {{ label: 'PMI',       data: {pmi_data},       borderColor: '#f39c12', backgroundColor: 'rgba(243,156,18,0.08)', fill: true, pointRadius: 0, tension: 0.3 }},
        ]
      }},
      options: {{
        plugins: {{ title: {{ display: true, text: 'Monthly Principal vs Interest vs PMI' }} }},
        scales: {{ y: {{ stacked: false, ticks: {{ callback: fmt }} }} }},
      }}
    }});

    // 3. Cumulative Payment vs Cumulative Interest
    new Chart(document.getElementById('cumulativeChart'), {{
      type: 'line',
      data: {{
        labels,
        datasets: [
          {{ label: 'Cumulative Payment', data: {cum_payment_data}, borderColor: '#8e44ad', backgroundColor: 'rgba(142,68,173,0.08)', fill: true, pointRadius: 0, tension: 0.3 }},
          {{ label: 'Cumulative Interest', data: {cum_interest_data}, borderColor: '#e74c3c', backgroundColor: 'rgba(231,76,60,0.08)', fill: true, pointRadius: 0, tension: 0.3 }},
        ]
      }},
      options: {{
        plugins: {{ title: {{ display: true, text: 'Cumulative Payment vs Cumulative Interest' }} }},
        scales: {{ y: {{ ticks: {{ callback: fmt }} }} }},
      }}
    }});

    // 4. Stacked monthly breakdown (principal + interest + pmi + insurance)
    const insData = Array({d['term_months']}).fill({d['homeowners_insurance']});
    new Chart(document.getElementById('monthlyBreakdownChart'), {{
      type: 'bar',
      data: {{
        labels,
        datasets: [
          {{ label: 'Principal', data: {principal_data}, backgroundColor: '#27ae60' }},
          {{ label: 'Interest',  data: {interest_data},  backgroundColor: '#e74c3c' }},
          {{ label: 'PMI',       data: {pmi_data},       backgroundColor: '#f39c12' }},
          {{ label: 'Insurance', data: insData,           backgroundColor: '#3498db' }},
        ]
      }},
      options: {{
        plugins: {{ title: {{ display: true, text: 'Monthly Payment Breakdown (Stacked)' }} }},
        scales: {{
          x: {{ stacked: true, ticks: {{ maxTicksLimit: 12 }} }},
          y: {{ stacked: true, ticks: {{ callback: fmt }} }},
        }},
      }}
    }});
  </script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)
    print(f"HTML report written to: {output_path}")


def run(
    home_value: float,
    down_payment: float,
    annual_rate: float,
    term_years: int,
    pmi: bool,
    pmi_rate: float,
    homeowners_insurance: float,
    show_table: bool,
    html: bool,
    html_output: str,
) -> None:
    data = amortize(home_value, down_payment, annual_rate, term_years, pmi, pmi_rate, homeowners_insurance)
    print_text(data, show_table=show_table)
    if html:
        generate_html(data, html_output)


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
    parser.add_argument(
        "--no-table",
        action="store_true",
        default=False,
        help="Suppress the amortization table, show summary only",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        default=False,
        help="Generate an HTML report with charts",
    )
    parser.add_argument(
        "--html-output",
        type=str,
        default="mortgage.html",
        metavar="FILE",
        help="Output filename for the HTML report",
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
        show_table=not args.no_table,
        html=args.html,
        html_output=args.html_output,
    )


if __name__ == "__main__":
    main()
