import sqlite3
import logging


logger = logging.getLogger(__name__)

DB_FILE = "archive.db"

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def init_db(self):
        """Создание таблицы при первом запуске"""
        try:
            self.conn = sqlite3.connect(DB_FILE)
            self.conn.row_factory = sqlite3.Row # Доступ по имени колонки
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    players INTEGER NOT NULL,
                    time INTEGER NOT NULL,
                    difficulty TEXT,
                    photo_path TEXT
                )
            """)
            self.conn.commit()
            logger.info("База данных инициализирована")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            return False

    def get_all(self):
        """Получение всех записей"""
        try:
            self.cursor.execute("""
                SELECT id, name, players, time, difficulty, photo_path
                FROM games ORDER BY name
            """)
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения записей: {e}")
            return []
          
    def insert_game(self, data):
        """Добавление игры"""
        try:
            self.cursor.execute("INSERT INTO games (name, players, time, difficulty, photo_path) VALUES (?, ?, ?, ?, ?)",
                       (data["name"], 
                        data["players"], 
                        data["time"], 
                        data["difficulty"], 
                        data["photo_path"]))
            self.conn.commit()
            logger.info(f"Игра '{data['name']}' добавлена")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления: {e}")
            self.conn.rollback()
            return False
        
    def delete_game(self, id):
        """Удаление игры"""
        try:
            self.cursor.execute("DELETE FROM games WHERE id=?", (id,))
            self.conn.commit()
            logger.info(f"Запись ID {id} удалена")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка удаления: {e}")
            self.conn.rollback()
            return False
        
    def get_filtered(self, min_players):
        """Применение фильтра"""
        try:
            self.cursor.execute("""
                SELECT id, name, players, time, difficulty, photo_path
                FROM games WHERE players <= ? ORDER BY name""", (min_players,))
            logger.info(f"Игры отфильтрованы")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка фильтрации: {e}")
            return []

        
        
        
   
        
    