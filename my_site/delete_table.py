import sqlite3

db_path = "remotedb.sqlite3"
table_name = "chat_guestuser"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Удаляем таблицу
cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
conn.commit()
conn.close()

print(f"✅ Таблица '{table_name}' удалена из базы '{db_path}'.")
