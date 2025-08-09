from gui import (
    create_order_form,
    view_orders,
    show_analysis_menu,
    show_product_menu,
    show_clients_menu
)
from db import initialize_db
import tkinter as tk

def main():
    """
    Запускает графическое приложение для управления заказами.

    Инициализирует базу данных, создаёт главное окно интерфейса и отображает
    кнопки для навигации по функциям: создание заказа, просмотр заказов,
    управление клиентами, управление товарами и аналитика.

    Notes
    -----
    - Использует модуль `tkinter` для создания GUI.
    - Все действия вызываются через соответствующие функции из модуля `gui`.
    - Перед запуском интерфейса вызывается `initialize_db()` для подготовки базы данных.
    """
    initialize_db()

    root = tk.Tk()
    root.title("Система управления заказами")

    # Размеры окна приложения
    window_width = 320
    window_height = 500

    # Получение размеров экрана
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Вычисление координат центра
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Установка геометрии с позиционированием для открытия окна приложения по центру экрана
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Кнопки меню действий
    tk.Label(root, text="Главное меню", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Button(root, text="Создать заказ", command=create_order_form, width=30).pack(pady=5)
    tk.Button(root, text="Просмотр заказов", command=view_orders, width=30).pack(pady=5)
    tk.Button(root, text="Работа с клиентами", command=show_clients_menu, width=30).pack(pady=5)
    tk.Button(root, text="Работа с товарами", command=show_product_menu, width=30).pack(pady=10)
    tk.Button(root, text="Аналитика", command=show_analysis_menu, width=30).pack(pady=10)

    # Запуск приложения
    root.mainloop()

if __name__ == "__main__":
    main()