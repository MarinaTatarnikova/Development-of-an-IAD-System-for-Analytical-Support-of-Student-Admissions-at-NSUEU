from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(
    'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniya_NGUEU?' +
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

tables = [
    'faculties', 'education_levels', 'competition_types',
    'study_forms', 'application_sources', 'application_statuses',
    'application_periods', 'programs', 'entrants',
    'education_documents', 'applications'
]

for table in tables:
    try:
        # Сначала узнаем размер таблицы
        count_result = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {table}", engine)
        count = count_result.iloc[0]['cnt']

        print(f"\n{table} (всего записей: {count}):")

        # Для больших таблиц ограничиваем вывод
        if count > 50:
            print(f"Показаны первые 50 из {count} записей:")
            data_result = pd.read_sql(f"SELECT TOP 50 * FROM {table}", engine)
        else:
            data_result = pd.read_sql(f"SELECT * FROM {table}", engine)

        if not data_result.empty:
            records = data_result.to_dict('records')
            for record in records:
                row_tuple = tuple(record.values())
                print(f"{row_tuple},")
        else:
            print("Таблица пуста")

    except Exception as e:
        print(f"Ошибка при выводе {table}: {e}")