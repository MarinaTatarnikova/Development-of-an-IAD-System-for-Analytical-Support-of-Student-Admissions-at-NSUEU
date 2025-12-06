import pandas as pd
from sqlalchemy import create_engine, inspect, text

def check_data_integrity(engine, table_name, df, inspector):
    issues = []

    # 1. Проверка первичного ключа
    pk = inspector.get_pk_constraint(table_name)["constrained_columns"]
    if pk and df.duplicated(subset=pk, keep=False).any():
        issues.append(f"Дублирование первичного ключа: {pk}")

    # 2. Проверка внешних ключей
    for fk in inspector.get_foreign_keys(table_name):
        col = fk["constrained_columns"][0]
        ref_table = fk["referred_table"]
        ref_col = fk["referred_columns"][0]
        ref_df = pd.read_sql(f"SELECT {ref_col} FROM {ref_table}", engine)
        missing = ~df[col].isin(ref_df[ref_col])
        if missing.any():
            issues.append(f"Неверные внешние ключи: {col} -> {ref_table}.{ref_col}")

    # 3. Проверка типов данных
    for col in inspector.get_columns(table_name):
        name = col["name"]
        sql_type = str(col["type"]).lower()
        if name not in df.columns:
            issues.append(f"Столбец отсутствует: {name}")
            continue
        if "int" in sql_type and not pd.api.types.is_integer_dtype(df[name]):
            issues.append(f"Тип должен быть INT: {name}")
        if ("char" in sql_type or "text" in sql_type) and not pd.api.types.is_string_dtype(df[name]):
            issues.append(f"Тип должен быть TEXT: {name}")
        if "date" in sql_type and not pd.api.types.is_datetime64_any_dtype(df[name]):
            issues.append(f"Тип должен быть DATE: {name}")

    # 4. Логическая проверка данных
    for col in df.select_dtypes(include=["int64", "float64"]).columns:
        if (df[col] < 0).any():
            issues.append(f"Отрицательные значения: {col}")
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            if (df[col] > pd.Timestamp.today()).any():
                issues.append(f"Дата из будущего: {col}")

    return issues

def data_cleaning_module():
    engine = create_engine(
        'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniya_NGUEU?'
        'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    )
    inspector = inspect(engine)

    tables_to_clean = [
        'application_choices', 'applications', 'entrants', 'education_documents',
        'programs', 'faculties', 'education_levels', 'application_statuses',
        'application_periods', 'application_sources', 'study_forms', 'competition_types'
    ]

    # Отключаем ограничения FK
    with engine.begin() as conn:
        conn.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'"))

    for table_name in tables_to_clean:
        print(f"\nОбработка таблицы: {table_name}")
        df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
        if df.empty:
            print("Таблица пуста")
            continue

        # Удаление дубликатов
        duplicates_count = df.duplicated().sum()
        df = df.drop_duplicates()
        print(f"Удалено дубликатов: {duplicates_count}")

        # Заполнение пропусков
        missing_before = df.isnull().sum().sum()
        for col in df.columns:
            if df[col].dtype in ['object', 'string']:
                df[col] = df[col].fillna('Не указано')
            elif df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
        missing_after = df.isnull().sum().sum()
        print(f"Пропущенные значения заполнены: {missing_before - missing_after}")

        # Проверка целостности данных
        issues = check_data_integrity(engine, table_name, df, inspector)
        if issues:
            print("Обнаружены проблемы:")
            for i in issues:
                print(" -", i)
        else:
            print("Все проверки пройдены")

        # Сохраняем очищенные данные обратно в базу данных
        with engine.begin() as conn:
            conn.execute(text(f"DELETE FROM {table_name}"))
            df.to_sql(table_name, conn, if_exists='append', index=False)


        print(f"Таблица {table_name} успешно сохранена в базе данных")

    # Включаем ограничения FK обратно
    with engine.begin() as conn:
        conn.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'"))

    print("\nОчистка и проверка данных завершена")

if __name__ == "__main__":
    data_cleaning_module()

