import unittest

from v2g_model import calculate, capital_recovery_factor, load_defaults


class V2GModelTests(unittest.TestCase):
    def setUp(self):
        self.config = load_defaults()

    def test_default_peak_event_respects_energy_and_power_limits(self):
        result = calculate(self.config)
        peak = result["peak_event"]
        self.assertEqual(peak["active_buses"], 14)
        self.assertAlmostEqual(peak["nameplate_export_capacity_kw"], 840)
        self.assertAlmostEqual(peak["export_energy_per_event_kwh"], 416.64)
        self.assertAlmostEqual(peak["average_export_power_kw"], 138.88)
        self.assertLessEqual(peak["average_export_power_kw"], peak["nameplate_export_capacity_kw"])

    def test_route_reserve_limits_discharge_energy(self):
        result = calculate(self.config, {"starting_soc": 0.80, "departure_soc": 0.80})
        self.assertEqual(result["peak_event"]["export_energy_per_event_kwh"], 0)

    def test_no_available_buses_produces_zero_event_and_regulation_value(self):
        result = calculate(self.config, {"available_buses": 0})
        self.assertEqual(result["peak_event"]["export_energy_per_event_kwh"], 0)
        self.assertEqual(result["regulation"]["scenarios"]["central"]["gross_revenue_usd"], 0)

    def test_event_duration_limits_average_power_but_not_energy(self):
        short = calculate(self.config, {"event_hours": 1})["peak_event"]
        long = calculate(self.config, {"event_hours": 6})["peak_event"]
        self.assertGreater(short["average_export_power_kw"], long["average_export_power_kw"])
        self.assertAlmostEqual(short["export_energy_per_event_kwh"], long["export_energy_per_event_kwh"])

    def test_regulation_price_cases_are_ordered(self):
        results = calculate(self.config)["regulation"]["scenarios"]
        self.assertLess(results["low"]["gross_revenue_usd"], results["central"]["gross_revenue_usd"])
        self.assertLess(results["central"]["gross_revenue_usd"], results["high"]["gross_revenue_usd"])

    def test_user_can_edit_historical_price_sensitivities(self):
        result = calculate(self.config, {"price_central": 10})
        self.assertEqual(result["regulation"]["scenarios"]["central"]["price_usd_per_mwh"], 10)
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            calculate(self.config, {"price_low": -1})

    def test_energy_loss_is_subtracted_once(self):
        central = calculate(self.config)["regulation"]["scenarios"]["central"]
        expected = (
            central["gross_revenue_usd"]
            - central["recharge_loss_cost_usd"]
            - central["aggregator_fee_usd"]
            - central["battery_wear_cost_usd"]
            - central["maintenance_cost_usd"]
        )
        self.assertAlmostEqual(central["operating_net_usd"], expected)

    def test_capital_recovery_factor(self):
        self.assertAlmostEqual(capital_recovery_factor(0, 10), 0.1)
        self.assertAlmostEqual(capital_recovery_factor(0.05, 10), 0.1295045749654566)

    def test_invalid_available_buses_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "exceed fleet"):
            calculate(self.config, {"available_buses": 15})

    def test_invalid_soc_order_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            calculate(self.config, {"starting_soc": 0.6, "departure_soc": 0.7})

    def test_transmission_upgrade_is_separate_and_editable(self):
        default = calculate(self.config)
        with_upgrade = calculate(self.config, {"transmission_upgrade_cost_usd": 100000})
        self.assertEqual(default["capital"]["transmission_upgrade_cost_usd"], None)
        self.assertEqual(with_upgrade["capital"]["transmission_upgrade_cost_usd"], 100000)
        self.assertAlmostEqual(
            with_upgrade["capital"]["annualized_capital_cost_usd"]
            - default["capital"]["annualized_capital_cost_usd"],
            100000 * capital_recovery_factor(0.05, 10),
        )


if __name__ == "__main__":
    unittest.main()
