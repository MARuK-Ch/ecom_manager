"""
Unit-тесты для анализа данных.
"""

import unittest
import seaborn as sns
from unittest.mock import patch, MagicMock
import pandas as pd
from analysis import safe_parse, client_stats, order_trend_from_db, sales_trend_monthly_change

class TestSafeParse(unittest.TestCase):
    def test_valid_string_list(self):
        s = "[{'name': 'Product A'}, {'name': 'Product B'}]"
        result = safe_parse(s)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Product A')

    def test_invalid_string(self):
        s = "not a list"
        result = safe_parse(s)
        self.assertEqual(result, [])

    def test_already_list(self):
        data = [{'name': 'Product A'}]
        result = safe_parse(data)
        self.assertEqual(result, data)

    def test_non_string_non_list(self):
        result = safe_parse(123)
        self.assertEqual(result, 123)


    def test_client_stats_aggregation(self):
        orders = [
            {'client': 'Alice', 'total': 100},
            {'client': 'Bob', 'total': 200},
            {'client': 'Alice', 'total': 150}
        ]
        stats = client_stats(orders)
        self.assertEqual(len(stats), 2)
        self.assertIn('Клиент', stats.columns)
        self.assertIn('Количество заказов', stats.columns)
        self.assertIn('Общая сумма', stats.columns)

        alice_row = stats[stats['Клиент'] == 'Alice'].iloc[0]
        self.assertEqual(alice_row['Количество заказов'], 2)
        self.assertEqual(alice_row['Общая сумма'], 250)

    @patch('analysis.sqlite3.connect')
    def test_order_trend_from_db_empty(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.execute.return_value.fetchall.return_value = []
        mock_conn.close.return_value = None

        with patch('analysis.pd.read_sql_query', return_value=pd.DataFrame()):
            with patch('builtins.print') as mock_print:
                order_trend_from_db()
                mock_print.assert_called_with("Нет данных — таблица заказов пуста.")

    @patch('analysis.sqlite3.connect')
    def test_sales_trend_monthly_change_empty(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.close.return_value = None

        with patch('analysis.pd.read_sql_query', return_value=pd.DataFrame()):
            with patch('builtins.print') as mock_print:
                sales_trend_monthly_change()
                mock_print.assert_called()


    @patch('analysis.sqlite3.connect')
    def test_order_trend_from_db_empty(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.execute.return_value.fetchall.return_value = []
        mock_conn.close.return_value = None

        with patch('analysis.pd.read_sql_query', return_value=pd.DataFrame()):
            with patch('builtins.print') as mock_print:
                order_trend_from_db()
                mock_print.assert_called_with("Нет данных — таблица заказов пуста.")

    @patch('analysis.sqlite3.connect')
    @patch('analysis.pd.read_sql_query')
    def test_sales_trend_monthly_change_empty(self, mock_read_sql, mock_connect):
        mock_read_sql.return_value = pd.DataFrame()
        with patch('builtins.print') as mock_print:
            sales_trend_monthly_change()
            mock_print.assert_called()


if __name__ == '__main__':
    unittest.main()