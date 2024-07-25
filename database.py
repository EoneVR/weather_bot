import sqlite3


class Database:
    def __init__(self):
        self.database = sqlite3.connect('weather.db', check_same_thread=False)
        self.create_users_table()
        self.create_weather_table()

    def manager(self, sql, *args,
                fetchone: bool = False,
                fetchall: bool = False,
                commit: bool = False):
        with self.database as db:
            cursor = db.cursor()
            cursor.execute(sql, args)
            if commit:
                result = db.commit()
            if fetchone:
                result = cursor.fetchone()
            if fetchall:
                result = cursor.fetchall()
            return result

    def create_users_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER UNIQUE,
        name TEXT,
        language TEXT
        )
        '''
        self.manager(sql, commit=True)

    def first_register_user(self, chat_id, name):
        sql = '''
        INSERT INTO users(chat_id, name) VALUES (?,?)
        '''
        self.manager(sql, chat_id, name, commit=True)

    def get_user_by_chat_id(self, chat_id):
        sql = '''
        SELECT * FROM users WHERE chat_id = ?
        '''
        return self.manager(sql, chat_id, fetchone=True)

    def set_user_language(self, chat_id, lang):
        user = self.get_user_by_chat_id(chat_id)
        if user:
            sql = '''
            UPDATE users SET language = ? WHERE chat_id = ?
            '''
            self.manager(sql, lang, chat_id, commit=True)
        else:
            sql = '''
            INSERT INTO users (chat_id, language) VALUES (?,?)
            '''
            self.manager(sql, chat_id, lang, commit=True)

    def get_user_language(self, chat_id):
        sql = '''
        SELECT language FROM users WHERE chat_id = ?
        '''
        result = self.manager(sql, chat_id, fetchone=True)
        if result:
            return result[0]
        return None

    def create_weather_table(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS weather(
        weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        temp FLOAT,
        description TEXT,
        humidity INTEGER,
        pressure INTEGER,
        wind_speed FLOAT,
        chat_id INTEGER REFERENCES users(chat_id),
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
        )
        '''
        self.manager(sql, commit=True)

    def insert_data(self, city, temp, description, humidity, pressure, wind_speed, chat_id):
        sql = '''
        INSERT INTO weather (city, temp, description, humidity, pressure, wind_speed, chat_id) 
        VALUES (?,?,?,?,?,?,?)
        '''
        self.manager(sql, city, temp, description, humidity, pressure, wind_speed, chat_id, commit=True)

    def get_history(self, chat_id):
        sql = '''
        SELECT * FROM weather
        WHERE chat_id = ? AND temp IS NOT NULL ORDER BY timestamp DESC
        LIMIT 5
        '''
        return self.manager(sql, chat_id, fetchall=True)
