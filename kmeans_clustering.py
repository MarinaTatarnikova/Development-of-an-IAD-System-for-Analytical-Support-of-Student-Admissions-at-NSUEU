import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from kneed import KneeLocator

# Подключение к базе
engine = create_engine(
    'mssql+pyodbc://localhost\\SQLEXPRESS/PriemnayaKampaniya_NGUEU?' +
    'driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
)
conn = engine.connect()

# SQL-запрос
query = """
SELECT p.program_id, p.program_name,
       AVG(ed.edu_document_average_mark) AS avg_document_mark,
       COUNT(ac.choice_id) AS num_applications
FROM application_choices ac
JOIN applications a ON ac.application_id = a.application_id
JOIN entrants e ON a.entrant_id = e.entrant_id
JOIN education_documents ed ON e.document_id = ed.document_id
JOIN programs p ON ac.program_id = p.program_id
GROUP BY p.program_id, p.program_name
ORDER BY avg_document_mark DESC
"""
program_marks_df = pd.read_sql(query, conn)
conn.close()

# Масштабирование
X = program_marks_df[['avg_document_mark', 'num_applications']]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Метод локтя
inertias = []
K = range(1, 11)
for k in K:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

# Автоматическое определение локтя
kneedle = KneeLocator(K, inertias, curve='convex', direction='decreasing')
optimal_k = kneedle.knee
print(f"Оптимальное число кластеров по методу локтя: {optimal_k}")

# Визуализация метода локтя
plt.figure(figsize=(6,4))
plt.plot(K, inertias, 'bo-', label='Сумма квадратов расстояний')
plt.axvline(optimal_k, color='red', linestyle='--', label=f'Оптимальное k = {optimal_k}')
plt.xlabel('Количество кластеров')
plt.ylabel('Сумма квадратов расстояний до центров')
plt.title('Метод локтя для программ')
plt.grid(True)
plt.legend()
plt.show()

# Кластеризация
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
program_marks_df['cluster'] = kmeans.fit_predict(X_scaled)

# Визуализация кластеров
plt.figure(figsize=(10,6))
palette = sns.color_palette('tab10', optimal_k)
for cluster in range(optimal_k):
    cluster_data = program_marks_df[program_marks_df['cluster'] == cluster]
    plt.scatter(cluster_data['avg_document_mark'], cluster_data['num_applications'],
                s=100, color=palette[cluster], label=f'Кластер {cluster+1}')

# Центроиды в исходной шкале (красные крестики, без подписей)
centroids_original = scaler.inverse_transform(kmeans.cluster_centers_)
plt.scatter(centroids_original[:,0], centroids_original[:,1], marker='x', color='red', s=200)

plt.xlabel('Средний балл документа')
plt.ylabel('Количество заявлений')
plt.title('Кластеры программ по среднему баллу и популярности')
plt.legend()
plt.grid(True)
plt.show()

# Вывод кластеров на консоль
print("\nРаспределение программ по кластерам:")
for cluster in range(optimal_k):
    cluster_data = program_marks_df[program_marks_df['cluster'] == cluster]
    avg_mark = cluster_data['avg_document_mark'].mean()
    avg_apps = cluster_data['num_applications'].mean()
    print(f"\nКластер {cluster+1}: Средний балл = {avg_mark:.2f}, Среднее число заявлений = {avg_apps:.0f}")
    print(cluster_data[['program_name', 'avg_document_mark', 'num_applications']].sort_values(
        by='num_applications', ascending=False))
