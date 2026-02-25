import sqlite3

conn = sqlite3.connect("quiz.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
telegram_id INTEGER PRIMARY KEY,
username TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS questions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
exam TEXT,
subject TEXT,
topic TEXT,
question TEXT,
option_a TEXT,
option_b TEXT,
option_c TEXT,
option_d TEXT,
answer TEXT,
explanation TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attempts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
question_id INTEGER,
selected TEXT,
correct INTEGER
)
""")

conn.commit()
