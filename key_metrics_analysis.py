import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

# Настройка шрифта для кириллицы
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams['figure.autolayout'] = True

# Подключение к базе данных
engine = create_engine(
    'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniyaa_NGUEU?' +
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)
conn = engine.connect()

query = """
SELECT p.program_id, p.program_name, p.level_id, p.faculty_id,
       f.faculty_short_name,
       AVG(ed.edu_document_average_mark) AS avg_document_mark,
       COUNT(ac.choice_id) AS num_applications,
       sf.form_name,
       ct.competition_type,
       src.source_name
FROM application_choices ac
JOIN applications a ON ac.application_id = a.application_id
JOIN entrants e ON a.entrant_id = e.entrant_id
JOIN education_documents ed ON e.document_id = ed.document_id
JOIN programs p ON ac.program_id = p.program_id
LEFT JOIN faculties f ON p.faculty_id = f.faculty_id
LEFT JOIN study_forms sf ON ac.form_id = sf.form_id
LEFT JOIN competition_types ct ON ac.competition_id = ct.competition_id
LEFT JOIN application_sources src ON ac.source_id = src.source_id
GROUP BY p.program_id, p.program_name, p.level_id, p.faculty_id, f.faculty_short_name, sf.form_name, ct.competition_type, src.source_name
"""
df = pd.read_sql(query, conn)
conn.close()

level_names = {1: 'Бакалавриат', 2: 'Магистратура', 3: 'Специалитет', 4: 'Аспирантура', 5: 'Среднее профессиональное'}
df['level_name'] = df['level_id'].map(level_names)

plots_dir = "plots"
os.makedirs(plots_dir, exist_ok=True)
plots = []

def add_labels(ax, vertical=True):
    for p in ax.patches:
        if vertical:
            height = p.get_height()
            ax.annotate(f'{int(height)}', (p.get_x() + p.get_width()/2, height),
                        ha='center', va='bottom', fontsize=8)
        else:
            width = p.get_width()
            ax.annotate(f'{int(width)}', (width, p.get_y() + p.get_height()/2),
                        ha='left', va='center', fontsize=8)

graphs = [
    ("Популярность факультетов", df.groupby('faculty_short_name')['num_applications'].sum().sort_values(ascending=False), 'plum', 'Факультет', 'Количество заявлений', True),
    ("Популярность уровней образования", df.groupby('level_name')['num_applications'].sum().sort_values(ascending=False), 'lightgreen', 'Уровень образования', 'Количество заявлений', True),
    ("Популярность форм обучения", df.groupby('form_name')['num_applications'].sum().sort_values(ascending=False), 'skyblue', 'Форма обучения', 'Количество заявлений', True),
    ("Популярность типов конкурса", df.groupby('competition_type')['num_applications'].sum().sort_values(ascending=False), 'lightcoral', 'Тип конкурса', 'Количество заявлений', True),
    ("Популярность источников подачи", df.groupby('source_name')['num_applications'].sum().sort_values(ascending=False), 'salmon', 'Источник подачи', 'Количество заявлений', True),
    ("20 самых популярных программ", df.groupby('program_name')['num_applications'].sum().sort_values(ascending=False).head(20), 'skyblue', 'Программа', 'Количество заявлений', False)
]

# Генерация графиков и сохранение путей в список
for title, data, color, xlabel, ylabel, vertical in graphs:
    plt.figure(figsize=(12, 6) if vertical else (12, 8))
    if vertical:
        ax = data.plot(kind='bar', color=color)
        add_labels(ax, vertical=True)
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
    else:
        ax = data.plot(kind='barh', color=color)
        add_labels(ax, vertical=False)
        plt.ylabel(xlabel, fontsize=12)
        plt.xlabel(ylabel, fontsize=12)
        plt.gca().invert_yaxis()
    plt.title(title, fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y' if vertical else 'x', linestyle='--', alpha=0.7)
    plt.tight_layout(pad=2.0)
    path = os.path.join(plots_dir, f"{title}.png")
    plt.savefig(path)
    plt.close()
    plots.append(path)

# Сохраняем список графиков в CSV
plots_df = pd.DataFrame({'path': plots})
plots_df.to_csv("plots_list.csv", index=False)

print(f"Графики сохранены в {plots_dir}/ и список путей записан в plots_list.csv")


