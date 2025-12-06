from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(
    'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniya_NGUEU?' +
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

excel_file = 'Приёмная кампания_НГУЭУ.xlsx'

tables_mapping = [
    ('Факультеты', 'faculties'),
    ('Уровни образования', 'education_levels'),
    ('Типы конкурса', 'competition_types'),
    ('Формы обучения', 'study_forms'),
    ('Источники подачи', 'application_sources'),
    ('Периоды подачи', 'application_periods'),
    ('Статусы заявлений', 'application_statuses'),
    ('Программы', 'programs'),
    ('Документы об образовании', 'education_documents'),
    ('Абитуриенты', 'entrants'),
    ('Заявления', 'applications'),
    ('Варианты заявлений', 'application_choices')
]

for sheet_name, table_name in tables_mapping:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df = df.dropna(how='all')
    df.columns = df.columns.str.strip().str.replace('\xa0', ' ')
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Данные из листа '{sheet_name}' загружены в таблицу '{table_name}'")

print("Все данные из Excel успешно загружены в базу данных!")