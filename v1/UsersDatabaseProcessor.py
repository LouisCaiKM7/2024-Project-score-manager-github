import sqlite3
import Constant

Conn = sqlite3.connect(Constant.Users, check_same_thread=False)
Cur = Conn.cursor()
Cur.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')
Cur.execute('''
CREATE TABLE IF NOT EXISTS Students(
    id TEXT NOT NULL,
    password TEXT NOT NULL)''')
Conn.commit()