import sqlite3
import customtkinter as ctk
from tkinter import messagebox

# Настройка темы оформления
ctk.set_appearance_mode("dark")  # "light" или "dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


def init_db():
    conn = sqlite3.connect('poputchik_gui_v1.db')
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
            seats INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (driver_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()


class PoputchikAppV1(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Сервис поиска попутчиков — Версия 1")
        self.geometry("600x500")
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

        title = ctk.CTkLabel(frame, text="Вход / Регистрация", font=("Arial", 24, "bold"))
        title.pack(pady=20)

        self.username_entry = ctk.CTkEntry(frame, placeholder_text="Логин", width=250)
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Пароль", show="*", width=250)
        self.password_entry.pack(pady=10)

        self.role_var = ctk.StringVar(value="driver")
        rb_driver = ctk.CTkRadioButton(frame, text="Водитель", variable=self.role_var, value="driver")
        rb_driver.pack(pady=5)
        rb_passenger = ctk.CTkRadioButton(frame, text="Пассажир", variable=self.role_var, value="passenger")
        rb_passenger.pack(pady=5)

        btn_login = ctk.CTkButton(frame, text="Войти", command=self.handle_login, width=250, fg_color="#1f538d")
        btn_login.pack(pady=10)

        btn_reg = ctk.CTkButton(frame, text="Зарегистрироваться", command=self.handle_register, width=250,
                                fg_color="#2ba14b", hover_color="#1f7a36")
        btn_reg.pack(pady=5)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        conn = sqlite3.connect('poputchik_gui_v1.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.current_user = user
            messagebox.showinfo("Успех", f"Добро пожаловать, {user[1]}!")
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
            conn = sqlite3.connect('poputchik_gui_v1.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "🎉 Регистрация успешна! Теперь вы можете войти.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует.")

    def show_main_menu(self):
        self.clear_frame()
        user_id, username, role = self.current_user

        # Верхняя панель пользователя
        top_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        top_bar.pack(fill="x", side="top")

        user_label = ctk.CTkLabel(top_bar, text=f"👤 {username} ({'Водитель' if role == 'driver' else 'Пассажир'})",
                                  font=("Arial", 14, "bold"))
        user_label.pack(side="left", padx=20, pady=10)

        btn_logout = ctk.CTkButton(top_bar, text="Выйти", width=80, fg_color="#c93b3b", hover_color="#a82e2e",
                                   command=self.logout)
        btn_logout.pack(side="right", padx=20, pady=10)

        # Контентная зона
        if role == 'driver':
            self.show_driver_menu()
        else:
            self.show_passenger_menu()

    def logout(self):
        self.current_user = None
        self.show_login_frame()

    def show_driver_menu(self):
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(pady=30, padx=30, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🚗 Создание новой поездки", font=("Arial", 18, "bold")).pack(pady=15)

        self.dep_entry = ctk.CTkEntry(frame, placeholder_text="Откуда", width=300)
        self.dep_entry.pack(pady=8)

        self.dest_entry = ctk.CTkEntry(frame, placeholder_text="Куда", width=300)
        self.dest_entry.pack(pady=8)

        self.seats_entry = ctk.CTkEntry(frame, placeholder_text="Количество мест", width=300)
        self.seats_entry.pack(pady=8)

        self.price_entry = ctk.CTkEntry(frame, placeholder_text="Цена за место (руб)", width=300)
        self.price_entry.pack(pady=8)

        btn_create = ctk.CTkButton(frame, text="Создать поездку", fg_color="#1f538d", width=300,
                                   command=self.handle_create_trip)
        btn_create.pack(pady=20)

    def handle_create_trip(self):
        try:
            dep = self.dep_entry.get().strip()
            dest = self.dest_entry.get().strip()
            seats = int(self.seats_entry.get().strip())
            price = float(self.price_entry.get().strip())

            if not dep or not dest:
                raise ValueError

            conn = sqlite3.connect('poputchik_gui_v1.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO trips (driver_id, departure, destination, seats, price) VALUES (?, ?, ?, ?, ?)",
                           (self.current_user[0], dep, dest, seats, price))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "🚗 Поездка успешно создана!")
            self.dep_entry.delete(0, 'end')
            self.dest_entry.delete(0, 'end')
            self.seats_entry.delete(0, 'end')
            self.price_entry.delete(0, 'end')
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "Заполните все поля корректно! Места должны быть целым числом, цена — числом.")

    def show_passenger_menu(self):
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="🗺️ Доступные поездки", font=("Arial", 18, "bold")).pack(pady=10)

        # Текстовое поле с прокруткой для списка поездок
        textbox = ctk.CTkTextbox(frame, width=520, height=320, font=("Courier New", 12))
        textbox.pack(pady=10, padx=10, fill="both", expand=True)

        conn = sqlite3.connect('poputchik_gui_v1.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT trips.id, users.username, trips.departure, trips.destination, trips.seats, trips.price 
            FROM trips 
            JOIN users ON trips.driver_id = users.id
        ''')
        trips = cursor.fetchall()
        conn.close()

        if not trips:
            textbox.insert("0.0", "Пока нет доступных поездок.")
        else:
            for t in trips:
                info = f"ID: {t[0]} | Водитель: {t[1]}\nМаршрут: {t[2]} -> {t[3]}\nМест: {t[4]} | Цена: {t[5]} руб.\n" + "-" * 40 + "\n"
                textbox.insert("end", info)
        textbox.configure(state="disabled")  # Запрещаем редактирование текста


if __name__ == "__main__":
    app = PoputchikAppV1()
    app.mainloop()
