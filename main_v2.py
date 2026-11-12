import sqlite3
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")  # Изменили тему на зеленую для финансовой версии


def init_db():
    conn = sqlite3.connect('poputchik_gui_v2.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id INTEGER,
            departure TEXT NOT NULL,
            destination TEXT NOT NULL,
            distance REAL NOT NULL,
            seats INTEGER NOT NULL,
            price_per_passenger REAL NOT NULL,
            driver_profit REAL NOT NULL,
            FOREIGN KEY (driver_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


def calculate_trip_economy(distance, seats, fuel_consumption=8.0, fuel_price=55.0):
    fuel_needed = (distance / 100) * fuel_consumption
    gas_cost = fuel_needed * fuel_price
    total_required_revenue = gas_cost * 1.5
    base_price_per_seat = total_required_revenue / seats

    if seats >= 3:
        price_per_passenger = round(base_price_per_seat * 0.85, 2)
    else:
        price_per_passenger = round(base_price_per_seat, 2)

    expected_profit = round((price_per_passenger * seats) - gas_cost, 2)
    return price_per_passenger, expected_profit, gas_cost


class PoputchikAppV2(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Сервис поиска попутчиков — Версия 2 (Экономика)")
        self.geometry("650x550")
        self.resizable(False, False)

        self.current_user = None
        init_db()
        self.show_login_frame()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_frame(self):
        self.clear_frame()
        frame = ctk.CTkFrame(self, width=400, height=400, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        title = ctk.CTkLabel(frame, text="Экономический расчет\nПопутчики v2", font=("Arial", 22, "bold"))
        title.pack(pady=20)

        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Логин", width=250)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Пароль", show="*", width=250)
        self.password_entry.pack(pady=10)

        self.role_var = ctk.StringVar(value="driver")
        rb_driver = ctk.CTkRadioButton(frame, text="Водитель (Расчет экономики)", variable=self.role_var,
                                       value="driver")
        rb_driver.pack(pady=5)
        rb_passenger = ctk.CTkRadioButton(frame, text="Пассажир (Поиск цен)", variable=self.role_var, value="passenger")
        rb_passenger.pack(pady=5)

        btn_login = ctk.CTkButton(frame, text="Войти", command=self.handle_login, width=250)
        btn_login.pack(pady=10)

        btn_reg = ctk.CTkButton(frame, text="Регистрация", command=self.handle_register, width=250, fg_color="#3a3a3a",
                                hover_color="#2b2b2b")
        btn_reg.pack(pady=5)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        conn = sqlite3.connect('poputchik_gui_v2.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.current_user = user
            self.show_main_menu()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def handle_register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showwarning("Внимание", "Заполните все поля!")
            return

        try:
            conn = sqlite3.connect('poputchik_gui_v2.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Регистрация успешна!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Логин занят.")

    def show_main_menu(self):
        self.clear_frame()
        user_id, username, role = self.current_user

        top_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        top_bar.pack(fill="x", side="top")

        user_label = ctk.CTkLabel(top_bar, text=f"👤 {username} ({role.upper()})", font=("Arial", 14, "bold"))
        user_label.pack(side="left", padx=20, pady=10)

        btn_logout = ctk.CTkButton(top_bar, text="Выйти", width=80, fg_color="#c93b3b", hover_color="#a82e2e",
                                   command=self.show_login_frame)
        btn_logout.pack(side="right", padx=20, pady=10)

        if role == 'driver':
            self.show_driver_menu()
        else:
            self.show_passenger_menu()

    def show_driver_menu(self):
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(pady=25, padx=25, fill="both", expand=True)

        ctk.CTkLabel(frame, text="📊 Создание поездки + Алгоритм расчета стоимости", font=("Arial", 16, "bold")).pack(
            pady=15)

        self.dep_entry = ctk.CTkEntry(frame, placeholder_text="Откуда", width=300)
        self.dep_entry.pack(pady=6)

        self.dest_entry = ctk.CTkEntry(frame, placeholder_text="Куда", width=300)
        self.dest_entry.pack(pady=6)

        self.dist_entry = ctk.CTkEntry(frame, placeholder_text="Расстояние (в км)", width=300)
        self.dist_entry.pack(pady=6)

        self.seats_entry = ctk.CTkEntry(frame, placeholder_text="Количество мест", width=300)
        self.seats_entry.pack(pady=6)

        btn_calc = ctk.CTkButton(frame, text="Просчитать экономику и создать", width=300, fg_color="#2ba14b",
                                 hover_color="#1f7a36", command=self.process_trip_economy)
        btn_calc.pack(pady=20)

    def process_trip_economy(self):
        try:
            dep = self.dep_entry.get().strip()
            dest = self.dest_entry.get().strip()
            distance = float(self.dist_entry.get().strip())
            seats = int(self.seats_entry.get().strip())

            if not dep or not dest: raise ValueError

            # Считаем по алгоритму эксперимента
            price_seat, profit, gas = calculate_trip_economy(distance, seats)

            # Создаем диалоговое красивое окно подтверждения
            confirm_text = (
                f"📊 РЕЗУЛЬТАТЫ РАСЧЕТА СИСТЕМЫ:\n\n"
                f"• Затраты на топливо: {gas:.2f} руб.\n"
                f"• Рекомендованная цена места: {price_seat} руб.\n"
                f"• Твоя чистая прибыль при полной посадке: {profit} руб.\n\n"
                f"Вы согласны с расчетом системы?"
            )

            if messagebox.askyesno("Вычислительный эксперимент", confirm_text):
                conn = sqlite3.connect('poputchik_gui_v2.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trips (driver_id, departure, destination, distance, seats, price_per_passenger, driver_profit) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (self.current_user[0], dep, dest, distance, seats, price_seat, profit))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "🚗 Поездка успешно сохранена в БД!")

                # Очистка полей
                for e in [self.dep_entry, self.dest_entry, self.dist_entry, self.seats_entry]: e.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "Пожалуйста, введите корректные данные.\nРасстояние и места должны быть числами.")

    def show_passenger_menu(self):
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🚗 Доступные умные поездки (с учетом скидок)", font=("Arial", 16, "bold")).pack(
            pady=10)

        textbox = ctk.CTkTextbox(frame, width=560, height=360, font=("Courier New", 12))
        textbox.pack(pady=10, padx=10, fill="both", expand=True)

        conn = sqlite3.connect('poputchik_gui_v2.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT trips.id, users.username, trips.departure, trips.destination, trips.distance, trips.seats, trips.price_per_passenger 
            FROM trips 
            JOIN users ON trips.driver_id = users.id
        ''')
        trips = cursor.fetchall()
        conn.close()

        if not trips:
            textbox.insert("0.0", "Пока нет доступных поездок с авторасчетом.")
        else:
            for t in trips:
                info = (f"ID: {t[0]} | Водитель: {t[1]}\n"
                        f"Маршрут: {t[2]} -> {t[3]} ({t[4]} км)\n"
                        f"Свободных мест: {t[5]} | Цена за кресло: {t[6]} руб.\n" + "=" * 45 + "\n")
                textbox.insert("end", info)
        textbox.configure(state="disabled")


if __name__ == "__main__":
    app = PoputchikAppV2()
    app.mainloop()
