from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import StockData
from .backtesting import backtest_strategy
import datetime
import json
from unittest.mock import patch

class BacktestingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create some sample data with more price variation
        self.symbol = 'TEST'
        dates = [datetime.date(2023, 1, i) for i in range(1, 32)]
        prices = [100, 102, 98, 103, 97, 105, 106, 104, 107, 108, 106, 110, 112, 111, 113, 115, 114, 116, 118, 117, 119, 121, 120, 122, 124, 123, 125, 127, 126, 128, 130]
        for date, price in zip(dates, prices):
            StockData.objects.create(symbol=self.symbol, date=date, open_price=price, high_price=price+1, low_price=price-1, close_price=price, volume=1000)

    def test_valid_backtest(self):
        result = backtest_strategy(self.symbol, 10000, 5, 10)
        self.assertIn('total_return', result)
        self.assertIn('max_drawdown', result)
        self.assertIn('trades_executed', result)
        self.assertGreater(result['trades_executed'], 0)

    def test_invalid_symbol(self):
        with self.assertRaises(ValidationError):
            backtest_strategy('INVALID', 10000, 5, 10)

    def test_invalid_initial_investment(self):
        with self.assertRaises(ValidationError):
            backtest_strategy(self.symbol, -1000, 5, 10)

    def test_invalid_ma_windows(self):
        with self.assertRaises(ValidationError):
            backtest_strategy(self.symbol, 10000, -5, 10)
        with self.assertRaises(ValidationError):
            backtest_strategy(self.symbol, 10000, 5, -10)

    def test_no_trades(self):
        # Set MA windows larger than our dataset to prevent any trades
        result = backtest_strategy(self.symbol, 10000, 100, 200)
        self.assertEqual(result['trades_executed'], 0)
        self.assertEqual(result['total_return'], 0.0)

    def test_all_in_trade(self):
        # Set MA windows to trigger trades
        result = backtest_strategy(self.symbol, 10000, 3, 5)
        self.assertGreater(result['trades_executed'], 0)

    def test_api_endpoint(self):
        url = reverse('run_backtest')
        data = {
            'symbol': self.symbol,
            'initial_investment': 10000,
            'buy_ma_window': 3,
            'sell_ma_window': 5
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertIn('total_return', result)
        self.assertIn('max_drawdown', result)
        self.assertIn('trades_executed', result)
        self.assertGreater(result['trades_executed'], 0)

    def test_api_endpoint_invalid_data(self):
        url = reverse('run_backtest')
        data = {
            'symbol': self.symbol,
            'initial_investment': -1000,  # Invalid
            'buy_ma_window': 5,
            'sell_ma_window': 10
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.content)
        self.assertIn('error', result)

    def test_api_endpoint_missing_data(self):
        url = reverse('run_backtest')
        data = {
            'symbol': self.symbol,
            'initial_investment': 10000,
            # Missing 'buy_ma_window' and 'sell_ma_window'
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.content)
        self.assertIn('error', result)



class ReportGenerationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.report_url = reverse('get_report')

    @patch('financial_data.views.generate_report')
    @patch('financial_data.views.generate_pdf_report')
    def test_get_report_json(self, mock_generate_pdf_report, mock_generate_report):
        mock_generate_report.return_value = (
            {
                'symbol': 'TEST',
                'start_date': '2023-01-01',
                'end_date': '2023-01-31',
                'initial_investment': 10000,
                'total_return': 0.0676,
                'max_drawdown': 0.0,
                'trades_executed': 4
            },
            None  # plot_buffer
        )

        response = self.client.post(
            self.report_url,
            data=json.dumps({
                'symbol': 'TEST',
                'start_date': '2023-01-01',
                'end_date': '2023-01-31',
                'initial_investment': 10000,
                'buy_ma_window': 5,
                'sell_ma_window': 10,
                'format': 'json'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(data['symbol'], 'TEST')
        self.assertEqual(data['total_return'], 0.0676)
        self.assertEqual(data['max_drawdown'], 0.0)
        self.assertEqual(data['trades_executed'], 4)

    @patch('financial_data.views.generate_report')
    @patch('financial_data.views.generate_pdf_report')
    def test_get_report_pdf(self, mock_generate_pdf_report, mock_generate_report):
        mock_generate_report.return_value = ({}, None)
        mock_generate_pdf_report.return_value = b'PDF content'

        response = self.client.post(
            self.report_url,
            data=json.dumps({
                'symbol': 'TEST',
                'start_date': '2023-01-01',
                'end_date': '2023-01-31',
                'initial_investment': 10000,
                'buy_ma_window': 5,
                'sell_ma_window': 10,
                'format': 'pdf'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="TEST_report.pdf"')

    def test_get_report_invalid_json(self):
        response = self.client.post(
            self.report_url,
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['error'], 'Invalid JSON in request body')

    def test_get_report_missing_parameters(self):
        response = self.client.post(
            self.report_url,
            data=json.dumps({'symbol': 'TEST'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue('Missing required parameter' in json.loads(response.content)['error'])

    @patch('financial_data.views.generate_report')
    def test_get_report_server_error(self, mock_generate_report):
        mock_generate_report.side_effect = Exception('Test error')

        response = self.client.post(
            self.report_url,
            data=json.dumps({
                'symbol': 'TEST',
                'start_date': '2023-01-01',
                'end_date': '2023-01-31',
                'initial_investment': 10000,
                'buy_ma_window': 5,
                'sell_ma_window': 10,
                'format': 'json'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.content)['error'], 'An unexpected error occurred')

