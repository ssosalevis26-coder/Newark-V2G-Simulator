import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from app import SimulatorHandler
from v2g_model import calculate, load_defaults


class ModelBoundaryTests(unittest.TestCase):
    def test_invalid_numbers(self):
        for key, value in [('bus_count', 1.5), ('events_per_year', True),
                           ('asset_life_years', 2.5), ('site_cost', float('inf')),
                           ('battery_kwh', float('nan')), ('regulation_power_kw', -1),
                           ('regulation_throughput_ratio', 1.1), ('available_hours_per_week', 169),
                           ('ac_incremental_cost_per_kw', -1), ('price_low', float('nan'))]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                calculate(load_defaults(), {key: value})

    def test_bid_respects_site_and_charger(self):
        for overrides, expected in [({'site_export_limit_kw': 70}, 70),
                                     ({'charger_kw': 2}, 28),
                                     ({'site_export_limit_kw': 0}, 0)]:
            self.assertEqual(calculate(load_defaults(), overrides)['regulation']['fleet_dispatch_equivalent_kw'], expected)

    def test_event_count_is_not_market_revenue(self):
        a = calculate(load_defaults())
        b = calculate(load_defaults(), {'events_per_year': 0, 'event_hours': 8})
        self.assertEqual(a['regulation'], b['regulation'])
        self.assertEqual(b['peak_event']['annual_export_energy_kwh'], 0)

    def test_capital_and_negative_net(self):
        r = calculate(load_defaults(), {'cost_case': 'dc_chargers_plus_site_proxy', 'price_central': 0})
        self.assertEqual(r['capital']['equipment_capex_usd'], 14 * 89930)
        self.assertIsNone(r['regulation']['scenarios']['central']['simple_payback_years'])
        self.assertLess(r['regulation']['scenarios']['central']['annualized_net_after_capital_usd'], 0)

    def test_default_money_against_independent_arithmetic(self):
        for case, price in [('low', 21.15), ('central', 36.26), ('high', 54.97)]:
            r = calculate(load_defaults())['regulation']['scenarios'][case]
            gross = price / 1000 * 6656 * 29 * 14
            losses = .0744 * 6656 * 29 * .26 * .1 * 14
            wear = 29 * .26 * 6656 * 14 * .03
            self.assertAlmostEqual(r['operating_net_usd'], gross * .85 - losses - wear)


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), SimulatorHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        try:
            connection.request(method, path, body, headers or {})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_static_and_docs(self):
        for path in ['/', '/app.js', '/styles.css', '/SOURCES.md', '/api/defaults']:
            with self.subTest(path=path):
                status, body = self.request('GET', path)
                self.assertEqual(status, 200)
                self.assertTrue(body)
        self.assertEqual(self.request('GET', '/missing')[0], 404)
        self.assertEqual(self.request('GET', '/%2e%2e/app.py')[0], 403)

    def test_success_and_errors(self):
        status, body = self.request('POST', '/api/calculate', '{}')
        self.assertEqual(status, 200)
        self.assertIsNone(json.loads(body)['capital']['transmission_upgrade_cost_usd'])
        for payload in ['{', '[]', '{"bus_count": 2.5}', '{"price_low": NaN}', '{"battery_kwh": null}']:
            with self.subTest(payload=payload):
                status, body = self.request('POST', '/api/calculate', payload)
                self.assertEqual(status, 400)
                self.assertIn('error', json.loads(body))
        self.assertEqual(self.request('POST', '/api/calculate', 'x' * 32001)[0], 400)
        self.assertEqual(self.request('POST', '/api/calculate', headers={'Content-Length': '-1'})[0], 400)
        self.assertEqual(self.request('POST', '/unknown', '{}')[0], 404)
