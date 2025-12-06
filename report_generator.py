import pandas as pd
from fpdf import FPDF
import os

# Загружаем список графиков
plots_file = "plots_list.csv"
plots_df = pd.read_csv(plots_file)

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Добавляем каждый график в PDF
for _, row in plots_df.iterrows():
    if os.path.exists(row['path']):  # проверка существования файла
        pdf.add_page()
        pdf.image(row['path'], x=10, y=10, w=190)
    else:
        print(f"Файл не найден: {row['path']}")

output_pdf = "Key_Metrics_Report.pdf"
pdf.output(output_pdf)
print(f"Отчет успешно сформирован: {output_pdf}")



