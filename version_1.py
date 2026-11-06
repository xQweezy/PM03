import sqlite3


def init_db():
    conn = sqlite3.connect('carpool.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, rating REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Trips (
        trip_id INTEGER PRIMARY KEY AUTOINCREMENT, driver_id INTEGER, 
        departure TEXT, destination TEXT, price_per_km REAL, seats INTEGER)''')
    conn.commit()
    conn.close()


def add_test_data():
    conn = sqlite3.connect('carpool.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users")
    cursor.execute("DELETE FROM Trips")

    # Большой список водителей (10 человек)
    drivers = [
        ('Алексей', 'driver', 4.9), ('Иван', 'driver', 4.2), ('Сергей', 'driver', 4.7),
        ('Дмитрий', 'driver', 3.9), ('Ольга', 'driver', 5.0), ('Анна', 'driver', 4.5),
        ('Михаил', 'driver', 4.8), ('Елена', 'driver', 4.1), ('Павел', 'driver', 4.6),
        ('Игорь', 'driver', 3.5)
    ]
    cursor.executemany("INSERT INTO Users (name, role, rating) VALUES (?, ?, ?)", drivers)

    # Большой список поездок по разным направлениям
    trips = [
        (1, 'Москва', 'Тверь', 5.0, 3),
        (2, 'Москва', 'Тверь', 3.5, 2),
        (3, 'Москва', 'Тверь', 4.2, 4),
        (4, 'Москва', 'Санкт-Петербург', 6.0, 3),
        (5, 'Москва', 'Санкт-Петербург', 4.5, 1),
        (6, 'Москва', 'Казань', 5.5, 3),
        (7, 'Москва', 'Казань', 3.8, 2),
        (8, 'Казань', 'Нижний Новгород', 4.0, 4),
        (9, 'Краснодар', 'Сочи', 7.0, 2),
        (10, 'Краснодар', 'Сочи', 5.0, 3)
    ]
    cursor.executemany(
        "INSERT INTO Trips (driver_id, departure, destination, price_per_km, seats) VALUES (?, ?, ?, ?, ?)", trips)

    conn.commit()
    conn.close()


def simple_search(departure, destination):
    conn = sqlite3.connect('carpool.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Trips WHERE departure=? AND destination=?", (departure, destination))
    results = cursor.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    init_db()
    add_test_data()
    print("Вывод Версии 1 (Поиск Москва -> Санкт-Петербург):")
    print(simple_search('Москва', 'Санкт-Петербург'))
