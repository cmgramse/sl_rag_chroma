import sqlite3
import bcrypt

class UserManager:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users
        (username TEXT PRIMARY KEY, password TEXT)
        ''')
        self.conn.commit()

    def create_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            return False
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
        self.conn.commit()
        return True

    def verify_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        if result:
            return bcrypt.checkpw(password.encode('utf-8'), result[0])
        return False