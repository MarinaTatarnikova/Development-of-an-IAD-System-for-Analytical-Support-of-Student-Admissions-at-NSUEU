import regression_analysis
import random_forest
import kmeans_clustering

def main():
    print("Запуск модуля regression_analysis...")
    regression_analysis.run_analysis()

    print("Запуск модуля random_forest...")
    random_forest.run_prediction()

    print("Запуск модуля kmeans_clustering...")
    kmeans_clustering.run_clustering()
    print("Анализ завершен.")

if __name__ == "__main__":
    main()
