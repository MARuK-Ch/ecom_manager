import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox, ttk
from models import Client, Order
from utils import validate_email, validate_phone, validate_address
from db import (
    save_client, save_order,
    load_clients, load_products,
    delete_order_by_index, export_orders_to_csv,
    connect, delete_client_by_name, load_orders,
    import_clients_from_csv
)
from analysis import (
    sales_trend_monthly_change,
    top_clients_from_db, show_client_stats,
    order_trend_from_db
)
import pandas as pd

# ========== Защита от повторного открытия окон ==========
opened_windows = {}

def open_unique_window(key, title, width=600, height=400):
    """
    Открывает уникальное окно Tkinter, если оно ещё не открыто.

    Параметры
    ----------
    key : str
        Уникальный идентификатор окна.
    title : str
        Заголовок окна.
    width : int, optional
        Ширина окна (по умолчанию 600).
    height : int, optional
        Высота окна (по умолчанию 400).

    Возвращает
    ----------
    tk.Toplevel или None
        Новое окно, либо None, если окно уже открыто.
    """
    if key in opened_windows and opened_windows[key].winfo_exists():
        opened_windows[key].lift()
        return None

    win = tk.Toplevel()
    win.title(title)
    opened_windows[key] = win

    #Центрирование окна
    win.update_idletasks()  # Обновляем размеры до размещения
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

    return win

# ========== Форма добавления клиента ==========
def create_client_form():
    """
    Открывает форму для добавления нового клиента.

    Вводятся имя, email, телефон и адрес. Выполняется валидация и сохранение клиента.
    """
    window = open_unique_window("client_form", "Добавить клиента")
    if window is None:
        return

    window.geometry("300x250")
    tk.Label(window, text="Имя").pack()
    name_entry = tk.Entry(window)
    name_entry.pack()

    tk.Label(window, text="Email").pack()
    email_entry = tk.Entry(window)
    email_entry.pack()

    tk.Label(window, text="Телефон").pack()
    phone_entry = tk.Entry(window)
    phone_entry.pack()

    tk.Label(window, text="Адрес").pack()
    address_entry = tk.Entry(window)
    address_entry.pack()


    def submit():
        name = name_entry.get().strip()
        email = email_entry.get().strip()
        phone = phone_entry.get().strip()
        address = address_entry.get().strip()

        errors = []
        if not name:
            errors.append("Имя обязательно")
        if not validate_email(email):
            errors.append("Неверный email")
        if not validate_phone(phone):
            errors.append("Неверный телефон")
        if not validate_address(address):
            errors.append("Неверный адрес")

        if errors:
            messagebox.showerror("Ошибка", "\n".join(errors))
            return

        client = Client(name=name, email=email, phone=phone, address=address)
        save_client(client)
        messagebox.showinfo("Успех", f"Клиент {name} добавлен")

        name_entry.delete(0, tk.END)
        email_entry.delete(0, tk.END)
        phone_entry.delete(0, tk.END)
        address_entry.delete(0, tk.END)

    tk.Button(window, text="Сохранить", command=submit).pack(pady=10)

# ========== Форма создания заказа ==========
def create_order_form():
    """
    Открывает форму для создания нового заказа.

    Позволяет выбрать клиента и товары, затем сохраняет заказ.
    """
    window = open_unique_window("order_form", "Создание заказа")
    if window is None:
        return

    clients = load_clients()
    products = load_products()
    if not products:
        tk.Label(window, text="Нет доступных товаров").pack()
        return

    tk.Label(window, text="Клиент").pack()
    client_combo = ttk.Combobox(window, values=[c.name for c in clients])
    client_combo.pack()

    tk.Label(window, text="Выберите товары").pack()
    product_listbox = tk.Listbox(window, selectmode=tk.MULTIPLE, height=10)
    for p in products:
        product_listbox.insert(tk.END, f"{p.name} — {p.price} руб.")
    product_listbox.pack()

    def submit_order():
        client_name = client_combo.get()
        selected = product_listbox.curselection()
        if not selected or not client_name:
            messagebox.showerror("Ошибка", "Выберите клиента и товары")
            return
        client = next(c for c in clients if c.name == client_name)
        selected_products = [products[i] for i in selected]
        order = Order(client_id=client.name, products=selected_products)
        save_order(order)
        messagebox.showinfo("Готово", f"Заказ сохранён: {order.total} руб.")
        window.destroy()

    tk.Button(window, text="Создать", command=submit_order).pack()

# ========== Просмотр заказов ==========
def view_orders():
    orders = load_orders()
    window = open_unique_window("view_orders", "Заказы")
    if window is None:
        return

    button_width = 30

    def show_orders(data):
        listbox.delete(0, tk.END)
        for o in data:
            listbox.insert(tk.END, f"{o['date']} | {o['client']} | {o['total']} руб.")

    def sort_total():
        show_orders(sorted(orders, key=lambda o: o["total"], reverse=True))

    def sort_date():
        show_orders(sorted(orders, key=lambda o: o["date"]))

    ttk.Button(window, text="Сорт. по сумме", command=sort_total, width=button_width).pack(pady=10)
    ttk.Button(window, text="Сорт. по дате", command=sort_date, width=button_width).pack(pady=10)
    ttk.Button(window, text="Удалить заказ", command=manage_orders, width=button_width).pack(pady=10)
    ttk.Button(window, text="Экспорт заказов (CSV)", command=export_orders, width=button_width).pack(pady=10)
    listbox = tk.Listbox(window, width=60)
    listbox.pack()
    show_orders(orders)

# ========== Управление заказами ==========
def manage_orders():
    """
    Открывает окно управления заказами.

    Позволяет просматривать и удалять заказы из базы данных.
    """
    orders = load_orders()
    window = open_unique_window("manage_orders", "Управление заказами")
    if window is None:
        return

    listbox = tk.Listbox(window, width=60)
    listbox.pack()

    def refresh():
        listbox.delete(0, tk.END)
        for i, o in enumerate(orders):
            listbox.insert(tk.END, f"{i+1}) {o['date']} | {o['client']} | {o['total']} руб.")

    def delete_order():
        idx = listbox.curselection()
        if not idx:
            messagebox.showerror("Ошибка", "Выберите заказ")
            return
        delete_order_by_index(idx[0])
        orders.pop(idx[0])
        refresh()
        messagebox.showinfo("Удалено", "Заказ удалён")

    tk.Button(window, text="Удалить", command=delete_order).pack()
    refresh()

# ========== Меню анализа ==========
def show_analysis_menu():
    """
    Отображает меню анализа заказов.

    Предлагает выбор различных аналитических функций: статистика, динамика, топ-клиенты и т.д.
    """
    window = open_unique_window("analysis_menu", "Выберите анализ")
    if window is None:
        return

    orders = load_orders()
    if not orders:
        messagebox.showinfo("Анализ", "Нет данных для анализа")
        return

    df = pd.DataFrame(orders)

    button_width = 30

    ttk.Button(window, text="Статистика по клиентам", command=show_client_stats, width=button_width).pack(pady=5)
    ttk.Button(window, text="Топ-клиенты", command=top_clients_from_db, width=button_width).pack(pady=5)
    ttk.Button(window, text="Динамика заказов", command=order_trend_from_db, width=button_width).pack(pady=5)
    ttk.Button(window, text="Продажи по месяцам", command=sales_trend_monthly_change, width=button_width).pack(pady=5)
    ttk.Button(window, text="Закрыть", command=window.destroy, width=button_width).pack(pady=10)


# ========== Экспорт заказов ==========
def export_orders():
    export_orders_to_csv()
    messagebox.showinfo("Экспорт", "Файл orders_export.csv создан")

# ========== Добавление товара ==========
def create_product_form():
    """
    Открывает форму для добавления нового товара.

    Вводятся название, цена и категория. Выполняется валидация и сохранение в базу данных.
    """
    window = open_unique_window("product_form", "Добавить товар")
    if window is None:
        return

    window.geometry("300x220")
    tk.Label(window, text="Название").pack()
    name_entry = tk.Entry(window)
    name_entry.pack()

    tk.Label(window, text="Цена").pack()
    price_entry = tk.Entry(window)
    price_entry.pack()

    tk.Label(window, text="Категория").pack()
    category_entry = tk.Entry(window)
    category_entry.pack()

    def submit():
        name = name_entry.get().strip()
        price = price_entry.get().strip()
        category = category_entry.get().strip()

        errors = []
        if not name:
            errors.append("Название обязательно")
        try:
            price = float(price)
            if price <= 0:
                errors.append("Цена должна быть положительной")
        except ValueError:
            errors.append("Некорректная цена")
        if not category:
            errors.append("Категория обязательна")

        if errors:
            messagebox.showerror("Ошибка", "\n".join(errors))
            return

        conn = connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
            (name, price, category)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Готово", f"Товар '{name}' добавлен")
        name_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        category_entry.delete
        messagebox.showinfo("Готово", f"Товар '{name}' добавлен")
        name_entry.delete(0, tk.END)
        price_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)

    tk.Button(window, text="Сохранить", command=submit).pack(pady=10)

def manage_products():
    """
    Открывает окно для управления товарами.

    Позволяет просматривать список товаров и удалять выбранный товар из базы данных.
    """
    window = open_unique_window("manage_products", "Удалить товар")
    if window is None:
        return

    window.geometry("350x400")
    product_listbox = tk.Listbox(window, width=50)
    product_listbox.pack(pady=10)

    def refresh_list():
        product_listbox.delete(0, tk.END)
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, category FROM products")
        rows = cursor.fetchall()
        conn.close()
        for row in rows:
            product_listbox.insert(tk.END, f"{row[0]}) {row[1]} — {row[2]} руб. ({row[3]})")

    def delete_product():
        selected = product_listbox.curselection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите товар для удаления")
            return
        item_text = product_listbox.get(selected[0])
        product_id = int(item_text.split(")")[0])
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Удалено", f"Товар ID {product_id} удалён")
        refresh_list()

    tk.Button(window, text="Удалить выбранный товар", command=delete_product).pack(pady=5)
    refresh_list()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Управление заказами")
    root.geometry("400x600")

    # Кнопки меню

    tk.Button(root, text="Добавить товар", command=create_product_form).pack(pady=5)
    tk.Button(root, text="Создать заказ", command=create_order_form).pack(pady=5)
    tk.Button(root, text="Просмотр заказов", command=view_orders).pack(pady=5)
    tk.Button(root, text="Управление заказами", command=manage_orders).pack(pady=5)
    tk.Button(root, text="Статистика клиентов", command=show_client_stats).pack(pady=5)
    tk.Button(root, text="Аналитика", command=show_analysis_menu).pack(pady=10)
    tk.Button(root, text="Экспорт заказов", command=export_orders).pack(pady=10)

    root.mainloop()

def show_product_menu():
    """
    Отображает меню управления товарами.

    Предлагает действия: добавить товар, удалить товар, закрыть окно.
    """
    window = open_unique_window("product_menu", "Работа с товарами")
    if window is None:
        return

    button_width = 25

    ttk.Button(window, text="Добавить товар", command=create_product_form, width=button_width).pack(pady=19)
    ttk.Button(window, text="Удалить товар", command=manage_products, width=button_width).pack(pady=19)
    ttk.Button(window, text="Закрыть", command=window.destroy, width=button_width).pack(pady=19)


def show_clients_menu():
    """
    Отображает меню управления клиентами.

    Предлагает действия: добавить клиента, загрузить CSV, показать список клиентов.
    """
    window = open_unique_window("clients_menu", "Работа с клиентами")
    if window is None:
        return

    button_width = 25

    ttk.Button(window, text="Добавить клиента", command=create_client_form, width=39).pack(pady=19)
    ttk.Button(window, text="Загрузить список клиентов в формате csv", command=import_clients_from_csv, width=39).pack(pady=19)
    ttk.Button(window, text="Список клиентов", command=show_client_list, width=39).pack(pady=19)



def show_client_list():
    """
    Отображает список клиентов с возможностью поиска, удаления и экспорта.

    Реализует таблицу с данными клиентов, поиск по всем полям, удаление и экспорт в CSV/JSON.
    """
    clients = load_clients()
    if not clients:
        messagebox.showinfo("Список клиентов", "Нет данных")
        return

    window = open_unique_window("client_list", "Список клиентов")
    if window is None:
        return

    search_var = tk.StringVar()

    ttk.Label(window, text="Поиск клиента", font=("Arial", 10)).pack(pady=(10, 0))
    search_entry = ttk.Entry(window, textvariable=search_var, width=40)
    search_entry.pack(pady=5)

    # Таблица с 4 колонками
    columns = ("name", "email", "phone", "address")
    tree = ttk.Treeview(window, columns=columns, show="headings", selectmode="browse")
    tree.heading("name", text="Имя")
    tree.heading("email", text="Email")
    tree.heading("phone", text="Телефон")
    tree.heading("address", text="Адрес")

    # Настройка ширины колонок
    tree.column("name", width=150)
    tree.column("email", width=180)
    tree.column("phone", width=120)
    tree.column("address", width=200)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Заполнение таблицы
    def populate_tree(data):
        tree.delete(*tree.get_children())
        for client in data:
            tree.insert("", "end", values=(
                client.name,
                client.email,
                client.phone,
                client.address
            ))

    populate_tree(clients)

    # Поиск по всем полям
    def update_search(*args):
        query = search_var.get().lower()
        filtered = [
            client for client in clients
            if query in client.name.lower()
               or query in client.email.lower()
               or query in client.phone.lower()
               or query in client.address.lower()
        ]
        populate_tree(filtered)

    def reset_search():
        search_var.set("")
        populate_tree(clients)

    search_var.trace_add("write", update_search)

    ttk.Button(window, text="Сбросить поиск", command=reset_search).pack(pady=5)

    # Удаление выбранного клиента
    def delete_selected():
        """
        Удаляет выбранного клиента из таблицы и базы данных.

        Запрашивает подтверждение, удаляет клиента и обновляет таблицу.
        """
        selected_item = tree.selection()
        if selected_item:
            client_name = tree.item(selected_item)["values"][0]

            confirm = messagebox.askyesno("Удаление", f"Удалить клиента «{client_name}» из базы?")
            if not confirm:
                return

            # Удаляем из базы
            delete_client_by_name(client_name)

            # Обновляем список
            updated_clients = [c.name for c in load_clients()]
            original_clients.clear()
            original_clients.extend(updated_clients)
            populate_tree(original_clients)

            messagebox.showinfo("Удалено", f"Клиент «{client_name}» удалён.")
        else:
            messagebox.showwarning("Удаление", "Выберите строку")

    # Экспорт CSV
    def export_csv():
        """
        Экспортирует список клиентов в CSV-файл.

        Сохраняет файл с именами клиентов, выбранными из таблицы.
        """
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            result = [tree.item(item)["values"][0] for item in tree.get_children()]
            pd.DataFrame(result, columns=["client"]).to_csv(path, index=False)
            messagebox.showinfo("Экспорт", "Список сохранён в CSV")

    # Экспорт JSON
    def export_json():
        """
        Экспортирует список клиентов в JSON-файл.
        """
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            result = [tree.item(item)["values"][0] for item in tree.get_children()]
            pd.DataFrame(result, columns=["client"]).to_json(path, orient="records", force_ascii=False)
            messagebox.showinfo("Экспорт", "Список сохранён в JSON")

    # Кнопки управления
    btn_frame = ttk.Frame(window)
    btn_frame.pack(pady=5)

    ttk.Button(btn_frame, text="Удалить выбранного", command=delete_selected).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Экспорт CSV", command=export_csv).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Экспорт JSON", command=export_json).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Закрыть", command=window.destroy).pack(side="left", padx=5)