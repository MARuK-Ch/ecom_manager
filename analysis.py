import ast
import sqlite3
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from db import load_orders


def safe_parse(x):
    """
    Безопасно преобразует строку в объект Python.

    Параметры
    ----------
    x : str или любой тип
        Строка, содержащая литерал Python, либо другой объект.

    Возвращает
    ----------
    object
        Результат парсинга, либо пустой список, либо исходное значение.
    """
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except:
            return []
    return x


# ========== Статистика клиентов ==========
def show_client_stats():
    """
    Отображает статистику клиентов в новом окне Tkinter.

    Загружает данные заказов, вычисляет статистику по клиентам и выводит её в текстовом поле.
    """
    stats = client_stats(load_orders())
    from gui import open_unique_window
    window = open_unique_window("client_stats", "Статистика")
    if window is None:
        return

    text = tk.Text(window, width=60)
    text.pack()
    for _, row in stats.iterrows():
        text.insert(tk.END, f"{row['Клиент']}: {row['Количество заказов']} заказов, {row['Общая сумма']} руб.\n")

def top_clients_from_db():
    """
    Строит график ТОП-5 клиентов по количеству заказов.

    Загружает данные заказов, вычисляет статистику, выбирает 5 лучших клиентов и отображает график в окне.
    """
    stats = client_stats(load_orders())  # ← DataFrame с колонками: Клиент, Количество заказов, Общая сумма
    from gui import open_unique_window

    window = open_unique_window("client_stats", "Статистика клиентов", width=700, height=500)
    if window is None:
        return

    # Отбор ТОП-5 клиентов
    top_stats = stats.sort_values(by="Количество заказов", ascending=False).head(5)

    # Построение графика
    fig = Figure(figsize=(6, 4), dpi=100)
    fig.subplots_adjust(bottom=0.25)
    ax = fig.add_subplot(111)
    ax.bar(top_stats["Клиент"], top_stats["Количество заказов"], color="skyblue", width=0.9)
    ax.set_title("ТОП-5 клиентов по количеству заказов")
    ax.set_ylabel("Количество заказов")
    ax.set_xlabel("Клиенты")
    ax.tick_params(axis='x', rotation=45, labelsize=6)

    # Вставка графика в окно
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)



def order_trend_from_db():
    """
    Строит график количества заказов по дням за август 2025 года.

    Подключается к базе данных, извлекает даты заказов, фильтрует по августу 2025 и отображает график.
    """
    try:
        # Подключение к базе данных
        conn = sqlite3.connect("ecom.db")
        query = "SELECT date FROM orders"
        df = pd.read_sql_query(query, conn)
        conn.close()
    except Exception as e:
        print(f"Ошибка при загрузке данных из базы: {e}")
        return

    if df.empty:
        print("Нет данных — таблица заказов пуста.")
        return

    # Обработка дат
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    # Фильтрация на август 2025
    august_df = df[
        (df['date'].dt.year == 2025) &
        (df['date'].dt.month == 8)
    ]

    if august_df.empty:
        print("Нет заказов за август 2025.")
        return

    # Извлечение дня месяца
    august_df['day'] = august_df['date'].dt.day

    # Подсчёт заказов по дням
    daily_orders = august_df.groupby('day').size().reindex(range(1, 32), fill_value=0).reset_index(name='order_count')

    # Построение графика
    plt.figure(figsize=(12, 6))
    plt.plot(daily_orders['day'], daily_orders['order_count'], marker='o')

    plt.title("Количество заказов по дням — Август 2025")
    plt.xlabel("День месяца")
    plt.ylabel("Количество заказов")
    plt.xticks(ticks=range(1, 32))
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def client_stats(orders):
    """
    Вычисляет статистику по клиентам на основе списка заказов.

    Параметры
    ----------
    orders : list of dict
        Список заказов, где каждый элемент содержит поля 'client' и 'total'.

    Возвращает
    ----------
    pandas.DataFrame
        Таблица с колонками: 'Клиент', 'Количество заказов', 'Общая сумма'.
    """
    df = pd.DataFrame(orders)
    stats = df.groupby('client').agg({"total": ["count", "sum"]}).reset_index()
    stats.columns = ["Клиент", "Количество заказов", "Общая сумма"]
    return stats


def sales_trend_monthly_change():
    """
    Строит график общей суммы продаж по месяцам.

    Загружает данные из базы, агрегирует суммы по месяцам и отображает график с использованием seaborn.
    """
    try:
        conn = sqlite3.connect("ecom.db")
        query = "SELECT date, total FROM orders"
        df = pd.read_sql_query(query, conn)
        try:
            conn.close()
        except:
            pass  # игнорируем ошибку при закрытии мок-объекта
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return

    if df.empty:
        print("Нет данных — таблица заказов пуста.")
        return

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    df['month'] = df['date'].dt.month
    monthly_sales = df.groupby('month')['total'].sum().reset_index()

    plt.figure(figsize=(10, 6))
    sns.lineplot(x=monthly_sales['month'], y=monthly_sales['total'], marker='o')

    plt.title("Общая сумма продаж по месяцам, руб.")
    plt.xlabel("Месяц")
    plt.ylabel("Сумма продаж, руб")
    plt.xticks(ticks=range(1, 13), labels=[
        "Янв", "Фев", "Мар", "Апр", "Май", "Июн",
        "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"
    ])
    plt.ylim(bottom=0)
    plt.grid(True)
    plt.tight_layout()
    plt.show()