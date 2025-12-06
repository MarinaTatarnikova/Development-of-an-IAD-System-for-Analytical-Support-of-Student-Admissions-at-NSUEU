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
    'education_documents', 'applications', 'application_choices'
]

print("Количество записей в таблицах:")

for table in tables:
    count = pd.read_sql(f"SELECT COUNT(*) as cnt FROM {table}", engine).iloc[0]['cnt']
    print(f"{table}: {count}")