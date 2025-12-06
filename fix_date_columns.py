import pandas as pd
from sqlalchemy import create_engine, text

def fix_date_columns():
    engine = create_engine(
        'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniya_NGUEU?'
        'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    )

    # Таблицы и столбцы с датами для исправления
    date_fixes = {
        "education_documents": ["edu_document_issuance_date"],
        "application_periods": ["date_from", "date_to"]
    }

    print("\nИсправления проблем с форматами дат")

    for table, cols in date_fixes.items():
        print(f"\nОбработка таблицы: {table}")

        for col in cols:
            update_query = f"""
            UPDATE {table}
            SET {col} = TRY_CONVERT(DATE, {col})
            WHERE {col} IS NOT NULL
            """

            with engine.begin() as conn:
                conn.execute(text(update_query))

            print(f"Колонка {col} успешно приведена к типу DATE")

        print(f"Данные таблицы '{table}' обновлены и сохранены в базе данных")

    print("\nИсправление форматов дат завершено")
    print("Все изменения успешно применены и сохранены в SQL Server.")

if __name__ == "__main__":
    fix_date_columns()

