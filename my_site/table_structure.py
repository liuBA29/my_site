import sqlite3


def print_table_structure(db_path, table_name):
    print(f"\n=== Структура таблицы '{table_name}' в базе '{db_path}' ===")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    if columns:
        print(f"{'CID':<5} {'Name':<20} {'Type':<15} {'NotNull':<10} {'Default':<15} {'PK'}")
        print("-" * 80)
        for col in columns:
            cid, name, col_type, notnull, dflt_value, pk = col
            print(f"{cid:<5} {name:<20} {col_type:<15} {notnull:<10} {str(dflt_value):<15} {pk}")
    else:
        print(f"Таблица '{table_name}' не найдена.")

    conn.close()


# Пути к базам данных
db1 = "db.sqlite3"
db2 = "remotedb.sqlite3"
table = "chat_room"
table2 = "main_app_project"
table3 = "chat_message"

print_table_structure(db1, table3)
print_table_structure(db2, table3)

