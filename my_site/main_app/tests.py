from django.test import TestCase
import sqlite3

# Подключения к двум базам данных
source_conn = sqlite3.connect('remotedb.sqlite3')
target_conn = sqlite3.connect('db.sqlite3')

source_cursor = source_conn.cursor()
target_cursor = target_conn.cursor()

# Получаем все строки из remotedb
source_cursor.execute("SELECT * FROM main_app_project")
rows = source_cursor.fetchall()

# Определим, сколько столбцов в таблице
column_count = len(source_cursor.description)

# Составим плейсхолдеры вида (?, ?, ?, ...)
placeholders = ','.join(['?'] * column_count)

# Вставим данные в db.sqlite3
target_cursor.executemany(f"INSERT INTO main_app_project VALUES ({placeholders})", rows)

# Сохраняем изменения
target_conn.commit()

# Закрываем соединения
source_conn.close()
target_conn.close()

print("✅ Данные успешно скопированы.")

