import sqlite3

# Пути к базам
src_db = "remotedb.sqlite3"
dst_db = "db.sqlite3"
table = "main_app_usefulsoftware"

# Соединяемся
src_conn = sqlite3.connect(src_db)
dst_conn = sqlite3.connect(dst_db)

src_cursor = src_conn.cursor()
dst_cursor = dst_conn.cursor()

# Получаем список столбцов
src_cursor.execute(f"PRAGMA table_info({table})")
columns_info = src_cursor.fetchall()
column_names = [col[1] for col in columns_info]  # имена столбцов

columns_str = ", ".join(column_names)
placeholders = ", ".join("?" for _ in column_names)

# Получаем все строки из источника
src_cursor.execute(f"SELECT {columns_str} FROM {table}")
rows = src_cursor.fetchall()

# Очищаем таблицу назначения (по желанию)
dst_cursor.execute(f"DELETE FROM {table}")

# Вставляем данные
dst_cursor.executemany(
    f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})",
    rows
)

# Сохраняем и закрываем
dst_conn.commit()
src_conn.close()
dst_conn.close()

print("✅ Данные успешно скопированы.")
