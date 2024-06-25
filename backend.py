import sqlite3
import json
import time

DATABASE_PATH = "database.db"

def getuserid(username):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            cursor.execute("""SELECT id FROM users WHERE username = ?""", (username,))
            return cursor.fetchone()[0]
    except Exception as e:
        print("Error found:", e)
        return None

def get_db_connection():
    return sqlite3.connect(DATABASE_PATH)

def initialize():
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subzeddits (
                    link TEXT UNIQUE,
                    owner TEXT,
                    title TEXT,
                    description TEXT,
                    subscribers INT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    date_created INTEGER,
                    subzeddits BLOB
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subzeddit_link TEXT,
                    user_id INTEGER,
                    title TEXT,
                    content TEXT,
                    timestamp INTEGER,
                    FOREIGN KEY (subzeddit_link) REFERENCES subzeddits(link),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            dbcon.commit()
    except Exception as e:
        print("Error found:", e)
        
def createuser(username, password):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            user_data = {"subzeddits": []}
            user_data = json.dumps(user_data)
            user_data = bytes(user_data, 'utf-8')
            cursor.execute("""
                INSERT INTO users (username, password, date_created, subzeddits)
                VALUES (?, ?, ?, ?)
            """, (username, password, round(time.time() * 1000), user_data))
            dbcon.commit()
    except Exception as e:
        print("Error found:", e)
        
def login(username, password):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE username = ? AND password = ?
            """, (username, password))
            return cursor.fetchone() is not None
    except Exception as e:
        print("Error found:", e)
        return False
    
def createsubzeddit(link, owner, title, description):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            cursor.execute("""
                SELECT * FROM subzeddits WHERE link = ?
            """, (link,))
            if cursor.fetchone():
                print(f"Subzeddit with link '{link}' already exists.")
                return False
            cursor.execute("""
                INSERT INTO subzeddits (link, owner, title, description, subscribers)
                VALUES (?, ?, ?, ?, ?)
            """, (link, owner, title, description, 1))
            joinsubzeddit(link, owner)
            dbcon.commit()
            return True
    except Exception as e:
        print("Error found:", e)
        return False
        
def joinsubzeddit(link, username):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            cursor.execute("""
                SELECT * FROM subzeddits WHERE link = ?
            """, (link,))
            subzeddit = cursor.fetchone()
            if subzeddit is None:
                print(f"Subzeddit with link '{link}' does not exist.")
                return False
            cursor.execute("""
                UPDATE subzeddits SET subscribers = subscribers + 1 WHERE link = ?
            """, (link,))
            cursor.execute("SELECT subzeddits FROM users WHERE username = ?", (username,))
            binary_data = cursor.fetchone()[0]
            json_data = binary_data.decode("utf-8")
            json_data = json.loads(json_data)
            if link not in json_data["subzeddits"]:
                json_data["subzeddits"].append(link)
            json_data = json.dumps(json_data)
            json_data = bytes(json_data, 'utf-8')
            cursor.execute("UPDATE users SET subzeddits = ? WHERE username = ?", (json_data, username))
            dbcon.commit()
            return True
    except Exception as e:
        print("Error found:", e)
        return False

def createpost(subzeddit_link, user_id, title, content):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            cursor.execute("""
                INSERT INTO posts (subzeddit_link, user_id, title, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (subzeddit_link, user_id, title, content, round(time.time() * 1000))
            )
            dbcon.commit()
            return True
    except Exception as e:
        print("Error found:", e)
        return False
    
def getsubzeddit(link):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            cursor.execute("""
                SELECT * FROM subzeddits WHERE link = ?
            """, (link,))
            return cursor.fetchone()
    except Exception as e:
        print("Error found:", e)
        return None
    
def createpost(link, username, title, content):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            userid = getuserid(username)
            cursor.execute("""
                INSERT INTO posts (subzeddit_link, user_id, title, content, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (link, userid, title, content, round(time.time() * 1000))
            )
            dbcon.commit()
            return True
    except Exception as e:
        print("Error found:", e)
        return False
    
def getposts(link):
    try:
        with get_db_connection() as dbcon:
            cursor = dbcon.cursor()
            cursor.execute("""
                SELECT * FROM posts WHERE subzeddit_link = ?
            """, (link,))
            return cursor.fetchall()
    except Exception as e:
        print("Error found:", e)
        return None
