from datetime import datetime

class Entity:
    """Базовый класс с методом to_dict."""
    def to_dict(self):
        return self.__dict__

class Client(Entity):
    """Класс клиента интернет-магазина.

    Parameters
    ----------
    name : str
        Имя клиента.
    email : str
        Электронная почта.
    phone : str
        Телефон.
    address : str
        Адрес доставки.
    """
    def __init__(self, name, email, phone, address):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

class Product(Entity):
    """Класс товара.

    Parameters
    ----------
    name : str
        Название товара.
    price : float
        Цена товара.
    category : str
        Категория товара.
    """
    def __init__(self, name, price, category="Общие"):
        self.name = name
        self.price = price
        self.category = category

class Order(Entity):
    """Класс заказа.

    Parameters
    ----------
    client_id : str
        Имя или ID клиента.
    products : list of Product
        Список купленных товаров.
    date : datetime, optional
        Дата заказа.
    """
    def __init__(self, client_id, products, date=None):
        self.client_id = client_id
        self.products = products
        self.date = date or datetime.now().date()
        self.total = sum(p.price for p in products)
