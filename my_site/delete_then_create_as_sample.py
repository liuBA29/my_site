import sqlite3

db_path = "remotedb.sqlite3"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Удаляем таблицу, если она есть
cursor.execute("DROP TABLE IF EXISTS chat_message")

# Создаём заново с нужной структурой
cursor.execute("""
    CREATE TABLE chat_message (
        id INTEGER PRIMARY KEY NOT NULL,
        content TEXT NOT NULL,
        timestamp datetime NOT NULL,
        room_id bigint NOT NULL,
        user_id bigint NOT NULL
    )
""")

conn.commit()
conn.close()

print("✅ Таблица 'chat_message' пересоздана в 'remotedb.sqlite3' по образцу 'db.sqlite3'")
