import sqlite3


# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('poputchik.db')
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    # Таблица поездок
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


# --- ФУНКЦИОНАЛ ПРОГРАММЫ ---
def register_user(username, password, role):
    try:
        conn = sqlite3.connect('poputchik.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        print("🎉 Регистрация успешна!")
    except sqlite3.IntegrityError:
        print("❌ Ошибка: Пользователь с таким логином уже существует.")
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect('poputchik.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user  # Возвращает (id, username, role) или None


def create_trip(driver_id, departure, destination, seats, price):
    conn = sqlite3.connect('poputchik.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trips (driver_id, departure, destination, seats, price) VALUES (?, ?, ?, ?, ?)",
                   (driver_id, departure, destination, seats, price))
    conn.commit()
    conn.close()
    print("🚗 Поездка успешно создана!")


def view_trips():
    conn = sqlite3.connect('poputchik.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT trips.id, users.username, trips.departure, trips.destination, trips.seats, trips.price 
        FROM trips 
        JOIN users ON trips.driver_id = users.id
    ''')
    trips = cursor.fetchall()
    conn.close()
    return trips


# --- ГЛАВНОЕ МЕНЮ (Интерфейс Версии 1) ---
def main():
    init_db()
    current_user = None  # Тут будет храниться кортеж (id, username, role) после входа

    while True:
        if not current_user:
            print("\n=== Сервис поиска попутчиков (Версия 1) ===")
            print("1. Регистрация")
            print("2. Вход")
            print("3. Выход")
            choice = input("Выберите действие: ")

            if choice == '1':
                username = input("Придумайте логин: ")
                password = input("Придумайте пароль: ")
                role = input("Кто вы? (driver - водитель, passenger - попутчик): ").strip().lower()
                if role in ['driver', 'passenger']:
                    register_user(username, password, role)
                else:
                    print("❌ Неверная роль. Используйте driver или passenger.")
            elif choice == '2':
                username = input("Логин: ")
                password = input("Пароль: ")
                user_data = login_user(username, password)
                if user_data:
                    current_user = user_data
                    print(f"\n✅ Добро пожаловать, {current_user[1]}!")
                else:
                    print("❌ Неверный логин или пароль.")
            elif choice == '3':
                print("Программа завершена.")
                break
        else:
            user_id, username, role = current_user
            print(f"\n--- Меню пользователя: {username} ({role}) ---")
            if role == 'driver':
                print("1. Создать поездку")
                print("2. Выйти из аккаунта")
                choice = input("Действие: ")
                if choice == '1':
                    dep = input("Откуда: ")
                    dest = input("Куда: ")
                    seats = int(input("Количество мест: "))
                    price = float(input("Цена за место (руб): "))
                    create_trip(user_id, dep, dest, seats, price)
                elif choice == '2':
                    current_user = None

            elif role == 'passenger':
                print("1. Посмотреть доступные поездки")
                print("2. Выйти из аккаунта")
                choice = input("Действие: ")
                if choice == '1':
                    trips = view_trips()
                    print("\nДоступные поездки:")
                    if not trips:
                        print("Пока нет доступных поездок.")
                    for t in trips:
                        print(
                            f"ID: {t[0]} | Водитель: {t[1]} | Маршрут: {t[2]} -> {t[3]} | Мест: {t[4]} | Цена: {t[5]} руб.")
                elif choice == '2':
                    current_user = None


if __name__ == "__main__":
    main()
