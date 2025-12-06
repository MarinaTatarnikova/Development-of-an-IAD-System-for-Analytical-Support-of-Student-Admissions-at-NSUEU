from sqlalchemy import create_engine, inspect
import pandas as pd

engine = create_engine(
    'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniya_NGUEU?' +
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

inspector = inspect(engine)

# Получаем все таблицы из базы данных
all_tables = inspector.get_table_names()

# Исключаем системную таблицу
user_tables = [table for table in all_tables if not table.startswith('sys')]

print(f"Общее количество таблиц в базе данных: {len(user_tables)}\n")

for table_name in user_tables:
    df_check = pd.read_sql(f"SELECT TOP 1 * FROM {table_name}", engine)
    if not df_check.empty:
        print(f"Таблица '{table_name}' существует в базе данных.\nВ таблице '{table_name}' обнаружены данные.")
    else:
        print(f"Таблица '{table_name}' существует в базе данных, но она пуста.")