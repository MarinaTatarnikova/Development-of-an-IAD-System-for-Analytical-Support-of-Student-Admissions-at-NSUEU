import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# 1. Подключение к базе
engine = create_engine(
    'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniya_NGUEU?' +
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)

# 2. Получаем агрегированные данные
query = """
SELECT 
    p.level_id,
    p.faculty_id,
    ac.form_id,
    ac.competition_id,
    ac.source_id,
    ac.status_id,
    p.program_id,
    COUNT(*) AS application_count
FROM applications ap
JOIN application_choices ac ON ap.application_id = ac.application_id
JOIN programs p ON ac.program_id = p.program_id
GROUP BY 
    p.level_id, p.faculty_id, ac.form_id, ac.competition_id, ac.source_id, ac.status_id, p.program_id
"""
df = pd.read_sql(query, engine)

# 3. Получаем словари id -> названия для программ и факультетов
programs = pd.read_sql("SELECT program_id, program_name FROM programs", engine)
faculties = pd.read_sql("SELECT faculty_id, faculty_short_name FROM faculties", engine)

program_dict = dict(zip(programs['program_id'], programs['program_name']))
faculty_dict = dict(zip(faculties['faculty_id'], faculties['faculty_short_name']))

# 4. Кодируем категориальные признаки
cat_cols = ['level_id','faculty_id','form_id','competition_id','source_id','status_id','program_id']
df_enc = pd.get_dummies(df, columns=cat_cols, drop_first=True)

# 5. Разделяем признаки и target
X = df_enc.drop('application_count', axis=1)
y = df_enc['application_count']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Линейная регрессия
model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_pred = np.clip(y_pred, 0, None)  # убираем отрицательные прогнозы

#  7. Метрики
print("R²:", r2_score(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))

# 8. Топ факторов по коэффициентам
coefficients = pd.DataFrame({
    "feature": X.columns,
    "coefficient": model.coef_
})
coefficients['abs_coef'] = coefficients['coefficient'].abs()
coefficients['contrib_%'] = (coefficients['abs_coef'] / coefficients['abs_coef'].sum()) * 100

# 9. Заменяем id на реальные названия
def replace_id_with_name(feature_name):
    if feature_name.startswith('program_id_'):
        pid = int(feature_name.split('_')[-1])
        return program_dict.get(pid, feature_name)
    elif feature_name.startswith('faculty_id_'):
        fid = int(feature_name.split('_')[-1])
        return faculty_dict.get(fid, feature_name)
    else:
        return feature_name

coefficients['feature_name'] = coefficients['feature'].apply(replace_id_with_name)

# 10. Фильтруем только положительные коэффициенты и берём топ-10
top10_pos = coefficients[coefficients['coefficient'] > 0].sort_values('coefficient', ascending=False).head(10)
print("ТОП-10 факторов с реальными названиями:")
print(top10_pos[['feature_name','coefficient','contrib_%']])

# 11. График 1: фактические vs прогноз
plt.figure(figsize=(8,6))
plt.scatter(y_test, y_pred, alpha=0.7, color='blue', label='Прогнозы')
plt.plot([0, max(y_test)], [0, max(y_test)], 'r--', lw=2, label='Идеальная линия')
plt.xlabel('Фактическое количество заявлений')
plt.ylabel('Прогнозируемое количество заявлений')
plt.title('Фактические значения и прогнозы линейной регрессии')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

plt.figure(figsize=(14, 8))  # Увеличиваем высоту
plt.barh(top10_pos['feature_name'], top10_pos['contrib_%'], color='green')
plt.xlabel('Вклад в модель, %')
plt.title('ТОП-10 факторов, увеличивающих количество заявлений')
plt.gca().invert_yaxis()
plt.xticks(fontsize=10)
plt.yticks(fontsize=9)
plt.grid(True, axis='x', alpha=0.3)

# Добавляем отступы
plt.subplots_adjust(left=0.3, right=0.95, top=0.95, bottom=0.1)

plt.show()


