import sqlite3

DATABASE = "subete.db"

def init_tables(cursor, conn):
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, last_name TEXT, password TEXT, salt TEXT, is_admin INTEGER, created_at INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, class_id INTEGER, first_name TEXT, password TEXT, salt TEXT, created_at INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS score (id INTEGER PRIMARY KEY, student_id INTEGER, score INTEGER, elapsed INTEGER, created_at INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY, name TEXT, teacher_id INTEGER, created_at INTEGER)')
    conn.commit()

if __name__ == '__main__':
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    init_tables(cursor, conn)
    conn.close()