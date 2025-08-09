"""
Unit-тесты модуля models.py.
"""

import unittest
from datetime import datetime, date

# Импортируем классы
from models import Entity, Client, Product, Order

class TestEntity(unittest.TestCase):
    def test_to_dict(self):
        class Dummy(Entity):
            def __init__(self):
                self.x = 1
                self.y = "test"
        d = Dummy()
        result = d.to_dict()
        self.assertEqual(result, {'x': 1, 'y': 'test'})


class TestClient(unittest.TestCase):
    def test_client_creation(self):
        c = Client("Alice", "alice@example.com", "+123456789", "Wonderland")
        self.assertEqual(c.name, "Alice")
        self.assertEqual(c.email, "alice@example.com")
        self.assertEqual(c.phone, "+123456789")
        self.assertEqual(c.address, "Wonderland")

    def test_client_to_dict(self):
        c = Client("Bob", "bob@example.com", "987654321", "Nowhere")
        d = c.to_dict()
        self.assertEqual(d['name'], "Bob")
        self.assertEqual(d['email'], "bob@example.com")
        self.assertEqual(d['phone'], "987654321")
        self.assertEqual(d['address'], "Nowhere")


class TestProduct(unittest.TestCase):
    def test_product_creation(self):
        p = Product("Laptop", 999.99, "Электроника")
        self.assertEqual(p.name, "Laptop")
        self.assertEqual(p.price, 999.99)
        self.assertEqual(p.category, "Электроника")

    def test_default_category(self):
        p = Product("Book", 20.0)
        self.assertEqual(p.category, "Общие")

    def test_product_to_dict(self):
        p = Product("Pen", 1.5, "Канцелярия")
        d = p.to_dict()
        self.assertEqual(d['name'], "Pen")
        self.assertEqual(d['price'], 1.5)
        self.assertEqual(d['category'], "Канцелярия")


class TestOrder(unittest.TestCase):
    def test_order_creation_and_total(self):
        p1 = Product("Item1", 10.0)
        p2 = Product("Item2", 15.5)
        order = Order("client123", [p1, p2])
        self.assertEqual(order.client_id, "client123")
        self.assertEqual(order.total, 25.5)
        self.assertEqual(len(order.products), 2)

    def test_order_date_default(self):
        p = Product("Item", 5.0)
        order = Order("client456", [p])
        self.assertIsInstance(order.date, date)
        self.assertEqual(order.date, datetime.now().date())

    def test_order_to_dict(self):
        p = Product("Item", 5.0)
        order = Order("client789", [p], date=date(2025, 8, 9))
        d = order.to_dict()
        self.assertEqual(d['client_id'], "client789")
        self.assertEqual(d['total'], 5.0)
        self.assertEqual(d['date'], date(2025, 8, 9))
        self.assertIsInstance(d['products'], list)
        self.assertEqual(d['products'][0].name, "Item")


if __name__ == '__main__':
    unittest.main()
