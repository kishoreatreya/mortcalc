import unittest

import mortcalc


class MortgageCalculatorTests(unittest.TestCase):
    def test_pmi_not_charged_when_starting_ltv_is_at_threshold(self):
        data = mortcalc.amortize(500_000, 100_000, 6, 30, True, 0.5, 0)

        self.assertEqual(data["initial_monthly_pmi"], 0)
        self.assertIsNone(data["pmi_removed_month"])
        self.assertEqual(data["total_pmi_paid"], 0)
        self.assertTrue(all(row["pmi"] == 0 for row in data["rows"]))
        self.assertEqual(data["initial_monthly_payment"], data["pi_payment"])

    def test_pmi_is_charged_for_month_that_reaches_threshold(self):
        data = mortcalc.amortize(500_000, 50_000, 6, 30, True, 0.5, 0)
        monthly_pmi = 450_000 * 0.005 / 12

        self.assertEqual(data["pmi_removed_month"], 90)
        self.assertEqual(data["rows"][88]["month"], 89)
        self.assertEqual(data["rows"][88]["pmi"], monthly_pmi)
        self.assertEqual(data["rows"][89]["month"], 90)
        self.assertEqual(data["rows"][89]["pmi"], 0)
        self.assertEqual(data["total_pmi_paid"], monthly_pmi * 89)

    def test_invalid_inputs_raise_value_error(self):
        invalid_inputs = [
            (0, 0, 6, 30, False, 0.5, 0),
            (500_000, -1, 6, 30, False, 0.5, 0),
            (500_000, 500_000, 6, 30, False, 0.5, 0),
            (500_000, 50_000, -1, 30, False, 0.5, 0),
            (500_000, 50_000, 6, 0, False, 0.5, 0),
            (500_000, 50_000, 6, 30, False, 0.5, -1),
            (500_000, 50_000, 6, 30, True, 0, 0),
        ]

        for args in invalid_inputs:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    mortcalc.amortize(*args)


if __name__ == "__main__":
    unittest.main()
