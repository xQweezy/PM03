import sqlite3


# --- РАБОТА С БАЗОЙ ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('poputchik_v2.db')
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


# --- ВЫЧИСЛИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ (Расчет экономики поездки) ---
def calculate_trip_economy(distance, seats, fuel_consumption=8.0, fuel_price=55.0):
    """
    Вычислительный эксперимент: Расчет стоимости и окупаемости.
    Принимает: расстояние (км), количество мест.
    Считает: затраты на топливо, оптимальную стоимость для пассажира и прибыль водителя.
    """
    # 1. Расчет затрат водителя на бензин
    fuel_needed = (distance / 100) * fuel_consumption
    gas_cost = fuel_needed * fuel_price

    # 2. Определение базовой стоимости за всю поездку (затраты + 50% маржа водителя)
    total_required_revenue = gas_cost * 1.5

    # 3. Базовая цена за одно место при полной посадке
    base_price_per_seat = total_required_revenue / seats

    # 4. Динамическое ценообразование (Вычислительный эксперимент):
    # Если мест много (>= 3), попутчикам выгодно ехать вместе — даем скидку 15% на место,
    # так как водитель все равно отобьет стоимость за счет объема.
    if seats >= 3:
        price_per_passenger = round(base_price_per_seat * 0.85, 2)
    else:
        price_per_passenger = round(base_price_per_seat, 2)

    # 5. Ожидаемая чистая прибыль водителя при полной посадке (доход - расход на газ)
    expected_profit = round((price_per_passenger * seats) - gas_cost, 2)

    return price_per_passenger, expected_profit, gas_cost


# --- ФУНКЦИОНАЛ ПРОГРАММЫ ---
def register_user(username, password, role):
    try:
        conn = sqlite3.connect('poputchik_v2.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        print("🎉 Регистрация успешна!")
    except sqlite3.IntegrityError:
        print("❌ Ошибка: Пользователь с таким логином уже существует.")
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect('poputchik_v2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user


def create_trip(driver_id, departure, destination, distance, seats, price_per_passenger, driver_profit):
    conn = sqlite3.connect('poputchik_v2.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trips (driver_id, departure, destination, distance, seats, price_per_passenger, driver_profit) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (driver_id, departure, destination, distance, seats, price_per_passenger, driver_profit))
    conn.commit()
    conn.close()
    print("🚗 Поездка успешно создана и просчитана алгоритмом!")


def view_trips():
    conn = sqlite3.connect('poputchik_v2.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT trips.id, users.username, trips.departure, trips.destination, trips.distance, trips.seats, trips.price_per_passenger 
        FROM trips 
        JOIN users ON trips.driver_id = users.id
    ''')
    trips = cursor.fetchall()
    conn.close()
    return trips


# --- ГЛАВНОЕ МЕНЮ (Интерфейс Версии 2) ---
def main():
    init_db()
    current_user = None

    while True:
        if not current_user:
            print("\n=== Сервис поиска попутчиков (Версия 2: Вычислительный эксперимент) ===")
            print("1. Регистрация")
            print("2. Вход")
            print("3. Выход")
            choice = input("Выберите действие: ")

            if choice == '1':
                username = input("Придумайте логин: ")
                password = input("Придумайте пароль: ")
                role = input("Кто вы? (driver/passenger): ").strip().lower()
                if role in ['driver', 'passenger']:
                    register_user(username, password, role)
                else:
                    print("❌ Неверная роль.")
            elif choice == '2':
                username = input("Логин: ")
                password = input("Пароль: ")
                user_data = login_user(username, password)
                if user_data:
                    current_user = user_data
                    print(f"\n✅ Добро пожаловать, {current_user}!")
                else:
                    print("❌ Неверный логин или пароль.")
            elif choice == '3':
                break
        else:
            user_id, username, role = current_user
            print(f"\n--- Меню пользователя: {username} ({role}) ---")
            if role == 'driver':
                print("1. Создать поездку (с автоматическим расчетом стоимости)")
                print("2. Выйти из аккаунта")
                choice = input("Действие: ")
                if choice == '1':
                    dep = input("Откуда: ")
                    dest = input("Куда: ")
                    distance = float(input("Расстояние пути (в км): "))
                    seats = int(input("Сколько попутчиков возьмете (мест): "))

                    # Запуск вычислительного эксперимента перед сохранением
                    price_seat, profit, gas = calculate_trip_economy(distance, seats)

                    print(f"\n📊 --- Результаты расчета системы ---")
                    print(f"• Затраты на топливо составят: {gas:.2f} руб.")
                    print(f"• Рекомендованная цена для 1 пассажира: {price_seat} руб.")
                    print(f"• Твоя чистая прибыль при полной посадке: {profit} руб.")

                    confirm = input("Вы согласны с расчетом? (y/n): ").strip().lower()
                    if confirm == 'y':
                        create_trip(user_id, dep, dest, distance, seats, price_seat, profit)
                    else:
                        print("❌ Создание поездки отменено.")

                elif choice == '2':
                    current_user = None

            elif role == 'passenger':
                print("1. Посмотреть доступные поездки и цены")
                print("2. Выйти из аккаунта")
                choice = input("Действие: ")
                if choice == '1':
                    trips = view_trips()
                    print("\nДоступные попутные машины:")
                    if not trips:
                        print("Пока нет доступных поездок.")
                    for t in trips:
                        print(
                            f"ID: {t[0]} | Водитель: {t[1]} | Маршрут: {t[2]} -> {t[3]} ({t[4]} км) | Свободно мест: {t[5]} | Цена места: {t[6]} руб.")
                elif choice == '2':
                    current_user = None


if __name__ == "__main__":
    main()
