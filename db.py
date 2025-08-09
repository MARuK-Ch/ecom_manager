import sqlite3
from models import Client, Product, Order
from tkinter import filedialog, messagebox
import csv


DB_NAME = "ecom.db"

def connect():
    return sqlite3.connect(DB_NAME)
    """
    Устанавливает соединение с базой данных.

    Returns
    -------
    sqlite3.Connection
        Объект подключения к базе данных `ecom.db`.
    """

def save_client(client):
    """
    Сохраняет клиента в базу данных.

    Parameters
    ----------
    client : Client
        Объект клиента, содержащий имя, email, телефон и адрес.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT
    )""")
    cursor.execute("INSERT INTO clients (name, email, phone, address) VALUES (?, ?, ?, ?)",
                   (client.name, client.email, client.phone, client.address))
    conn.commit()
    conn.close()

def load_clients():
    """
    Загружает всех клиентов из базы данных.

    Returns
    -------
    list of Client
        Список объектов клиентов.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, phone, address FROM clients")
    rows = cursor.fetchall()
    conn.close()
    return [Client(name, email, phone, address) for name, email, phone, address in rows]

def save_order(order):
    """
    Сохраняет заказ в базу данных.

    Parameters
    ----------
    order : Order
        Объект заказа, содержащий ID клиента, список товаров, дату и общую сумму.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT,
        products TEXT,
        date TEXT,
        total REAL
    )""")
    product_list = ",".join([p.name for p in order.products])
    cursor.execute("INSERT INTO orders (client_id, products, date, total) VALUES (?, ?, ?, ?)",
                   (order.client_id, product_list, str(order.date), order.total))
    conn.commit()
    conn.close()

def load_orders():
    """
    Загружает все заказы из базы данных.

    Returns
    -------
    list of dict
        Список заказов в виде словарей с ключами: client, products, date, total.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, products, date, total FROM orders")
    rows = cursor.fetchall()
    conn.close()
    return [{"client": r[0], "products": r[1], "date": r[2], "total": r[3]} for r in rows]

def delete_order_by_index(index):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM orders LIMIT 1 OFFSET ?", (index,))
    row = cursor.fetchone()
    if row:
        cursor.execute("DELETE FROM orders WHERE id = ?", (row[0],))
    conn.commit()
    conn.close()

def export_orders_to_csv(filename="orders_export.csv"):
    """
    Экспортирует все заказы в CSV-файл.

    Parameters
    ----------
    filename : str, optional
        Имя файла для экспорта. По умолчанию "orders_export.csv".
    """
    import csv
    orders = load_orders()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["client", "products", "date", "total"])
        writer.writeheader()
        writer.writerows(orders)

def load_products():
    """
    Загружает все товары из базы данных.

    Returns
    -------
    list of Product
        Список объектов товаров.
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        category TEXT
    )""")
    cursor.execute("SELECT name, price, category FROM products")
    rows = cursor.fetchall()
    conn.close()
    return [Product(name, price, category) for name, price, category in rows]

def initialize_db():
    """
    Инициализирует структуру базы данных.

    Создаёт таблицы: clients, products, orders — если они ещё не существуют.
    """
    conn = connect()
    cursor = conn.cursor()

    # Таблица клиентов
    cursor.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT
    )""")

    # Таблица продуктов
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        category TEXT
    )""")

    # Таблица заказов
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id TEXT,
        products TEXT,
        date TEXT,
        total REAL
    )""")

    conn.commit()
    conn.close()


def delete_client_by_name(name):
    """
    Удаляет клиента по имени.

    Parameters
    ----------
    name : str
        Имя клиента, которого нужно удалить.
    """
    conn = connect()
    cursor = conn.cursor()
    print("Удаляем имя:", repr(name))
    cursor.execute("DELETE FROM clients WHERE name = ?", (name,))
    conn.commit()
    conn.close()

#Блок для импорта клиентов из CSV
#Подключение к существующей базе данных
conn = sqlite3.connect("ecom.db")
cursor = conn.cursor()


def add_client(name, email, phone, address):
    """
      Добавляет клиента в базу данных.

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
    cursor.execute("""
        INSERT INTO clients (name, email, phone, address)
        VALUES (?, ?, ?, ?)
    """, (name, email, phone, address))
    conn.commit()

#Импорт из CSV и сохранение в базу
def import_clients_from_csv():
    """
    Импортирует клиентов из CSV-файла.

    Notes
    -----
    - Открывает диалог выбора файла.
    - Загружает клиентов из CSV и сохраняет их в базу данных.
    - Показывает сообщение об успешном импорте или ошибке.
    """
    filepath = filedialog.askopenfilename(
        title="Выберите CSV файл",
        filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
    )
    if not filepath:
        return

    try:
        with open(filepath, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            imported = 0
            for row in reader:
                name = row.get("Имя", "").strip()
                email = row.get("Email", "").strip()
                phone = row.get("Телефон", "").strip()
                address = row.get("Адрес", "").strip()

                if name:  # Не добавляем пустые строки
                    add_client(name, email, phone, address)
                    print(f"Импортирован клиент: {name}, {email}, {phone}, {address}")
                    imported += 1

            messagebox.showinfo("Импорт завершён", f"Импортировано клиентов: {imported}")

    except Exception as e:
        messagebox.showerror("Ошибка импорта", f"Не удалось загрузить файл:\n{e}")