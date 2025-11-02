from sqlalchemy import create_engine
import pandas as pd

# Подключение к базе данных
engine = create_engine(
    'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniya_NGUEU?' +
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

# Читаем Excel файл
excel_file = 'Приёмная кампания_НГУЭУ.xlsx'

# Соответствие: русские названия листов Excel → английские названия таблиц БД
tables_mapping = {
    'Факультеты': 'faculties',
    'Уровни образования': 'education_levels',
    'Типы конкурса': 'competition_types',
    'Формы обучения': 'study_forms',
    'Источники подачи': 'application_sources',
    'Статусы заявлений': 'application_statuses',
    'Периоды подачи': 'application_periods',
    'Программы': 'programs',
    'Абитуриенты': 'entrants',
    'Документы об образовании': 'education_documents',
    'Заявления': 'applications'
}

# Переименование столбцов для конкретных таблиц
column_renames = {
    'entrants': {'gender': 'sex', 'full_name': 'fullfio'}
}

# Загружаем данные в каждую таблицу
for sheet_name, table_name in tables_mapping.items():
    try:
        # Читаем лист Excel
        df = pd.read_excel(excel_file, sheet_name=sheet_name)

        # ОЧИСТКА названий столбцов от невидимых символов
        df.columns = df.columns.str.strip()  # убираем пробелы по краям
        df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)  # заменяем множественные пробелы
        df.columns = df.columns.str.replace('\xa0', ' ')  # убираем неразрывные пробелы

        # Загружаем в БД
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Данные из листа '{sheet_name}' загружены в таблицу '{table_name}'")

    except Exception as e:
        print(f"Ошибка при загрузке {sheet_name} → {table_name}: {e}")

print("Все данные из Excel успешно загружены в базу данных!")