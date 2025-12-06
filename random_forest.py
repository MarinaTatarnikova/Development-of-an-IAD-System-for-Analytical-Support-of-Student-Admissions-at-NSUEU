import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import plot_tree
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt

# Подключение к базе
engine = create_engine(
    'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniyaa_NGUEU?' +
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

# Получаем данные
query = """
SELECT 
    ac.competition_id,
    p.level_id,
    ac.form_id,
    ac.source_id,
    ed.edu_document_average_mark
FROM application_choices ac
JOIN applications a ON ac.application_id = a.application_id
JOIN entrants e ON a.entrant_id = e.entrant_id
JOIN education_documents ed ON e.document_id = ed.document_id
JOIN programs p ON ac.program_id = p.program_id
WHERE ed.edu_document_average_mark IS NOT NULL
"""
df = pd.read_sql(query, engine)

# Словари для русских названий классов
class_labels_dict = {
    'competition_id': ['Договор', 'Бюджет', 'Квота'],
    'level_id': ['Бакалавриат', 'Магистратура', 'Специалитет', 'NULL'],
    'form_id': ['Очная', 'Заочная', 'Очно-заочная'],
    'source_id': ['ЕПГУ', 'Личный приём']
}

# Названия признаков
feature_names_rus = {
    'edu_document_average_mark': 'Средний балл документа',
    'level_id': 'Уровень образования',
    'form_id': 'Форма обучения',
    'source_id': 'Источник подачи'
}

# Названия целевых переменных для заголовков графиков
target_names_rus = {
    'competition_id': 'Типа конкурса',
    'level_id': 'Уровня образования',
    'form_id': 'Формы обучения',
    'source_id': 'Источника подачи'
}

# Функция для обучения, визуализации дерева, метрик и графика важности
def random_forest_plot(df, target_column, all_features, max_depth=3):
    # Исключаем целевой признак из признаков
    features_used = [f for f in all_features if f != target_column]

    X = df[features_used]
    y = df[target_column]

    # Разделяем на train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Выбираем одно дерево для визуализации
    tree = rf.estimators_[0]

    # Графическое дерево
    plt.figure(figsize=(20,10))
    plot_tree(
        tree,
        feature_names=[feature_names_rus[f] for f in features_used],
        class_names=class_labels_dict[target_column],
        filled=True,
        rounded=True,
        fontsize=10,
        max_depth=max_depth
    )
    plt.title(f"Фрагмент дерева для {target_names_rus[target_column]}")
    plt.show()

    # Предсказания и метрики
    y_pred = rf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

    print(f"\nМодель для {target_names_rus[target_column]}:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-score: {f1:.4f}")

    # Важность признаков
    importances = pd.DataFrame({
        'Признак': [feature_names_rus[f] for f in features_used],
        'Важность': rf.feature_importances_
    }).sort_values(by='Важность', ascending=False)
    print("Важность признаков:")
    for i, row in importances.iterrows():
        print(f"  {row['Признак']}: {row['Важность']:.4f}")

    # График важности признаков
    plt.figure(figsize=(6,4))
    plt.barh(importances['Признак'], importances['Важность'], color='skyblue')
    plt.xlabel('Важность')
    plt.title(f'Важность признаков для {target_names_rus[target_column]}')
    plt.gca().invert_yaxis()
    plt.grid(axis='x', alpha=0.3)
    plt.show()

    return rf, importances

#  Список всех признаков
all_features = ['level_id', 'form_id', 'source_id', 'edu_document_average_mark']

# 1. Тип конкурса
rf_comp, imp_comp = random_forest_plot(df, 'competition_id', all_features)

# 2. Уровень образования
rf_level, imp_level = random_forest_plot(df, 'level_id', all_features)

# 3. Форма обучения
rf_form, imp_form = random_forest_plot(df, 'form_id', all_features)

# 4. Источник подачи
rf_source, imp_source = random_forest_plot(df, 'source_id', all_features)

