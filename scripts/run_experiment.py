import os
import sys
import shutil
from datetime import datetime
import pandas as pd

# -------------------------------------------------
# Deney adı kontrolü
# -------------------------------------------------
if len(sys.argv) < 2:
    print("Kullanım: python3 run_experiment.py <experiment_name>")
    sys.exit(1)

experiment_name = sys.argv[1]
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Proje kök klasörü
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

data_dir = os.path.join(project_root, "data")
results_dir = os.path.join(project_root, "results")
experiments_dir = os.path.join(project_root, "experiments")

# Yeni deney klasörü
experiment_folder = os.path.join(experiments_dir, f"{experiment_name}_{timestamp}")
exp_data_dir = os.path.join(experiment_folder, "data")
exp_results_dir = os.path.join(experiment_folder, "results")

os.makedirs(exp_data_dir, exist_ok=True)
os.makedirs(exp_results_dir, exist_ok=True)

print("Deney klasörü oluşturuldu:")
print(experiment_folder)

# -------------------------------------------------
# Data dosyalarını kopyala
# -------------------------------------------------
data_files = [
    "ppg_raw_static.csv",
    "ppg_raw_motion.csv",
    "imu_motion.csv",
    "spo2_pr_log.csv",
]

for file_name in data_files:
    src = os.path.join(data_dir, file_name)
    dst = os.path.join(exp_data_dir, file_name)

    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Kopyalandı: data/{file_name}")
    else:
        print(f"Bulunamadı: data/{file_name}")

# -------------------------------------------------
# Results dosyalarını kopyala
# -------------------------------------------------
result_files = [
    "enhanced_fusion_table.csv",
    "enhanced_fusion.png",
    "classification_overlay.png",
    "motion_vs_reliability.png",
    "static_vs_motion_reliability.png",
    "hr_extraction.png",
    "vital_measurement_gate_with_motion.png",
    "vital_measurement_gate_table.csv",
]

for file_name in result_files:
    src = os.path.join(results_dir, file_name)
    dst = os.path.join(exp_results_dir, file_name)

    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Kopyalandı: results/{file_name}")
    else:
        print(f"Bulunamadı: results/{file_name}")

# -------------------------------------------------
# Küçük özet üret
# -------------------------------------------------
summary_path = os.path.join(experiment_folder, "summary.txt")

with open(summary_path, "w", encoding="utf-8") as f:
    f.write("Experiment Summary\n")
    f.write("==================\n")
    f.write(f"Experiment name: {experiment_name}\n")
    f.write(f"Timestamp: {timestamp}\n\n")

    gate_table = os.path.join(results_dir, "vital_measurement_gate_table.csv")
    if os.path.exists(gate_table):
        df = pd.read_csv(gate_table)

        f.write("Decision Counts:\n")
        f.write(str(df["decision"].value_counts()))
        f.write("\n\n")

        f.write(f"Mean final reliability: {df['final_reliability'].mean():.3f}\n")
        f.write(f"Mean displayed SpO2: {df['display_spo2'].mean():.2f}\n")
        f.write(f"Mean displayed PR: {df['display_pr'].mean():.2f}\n")
    else:
        f.write("vital_measurement_gate_table.csv bulunamadı.\n")

print(f"\nÖzet kaydedildi: {summary_path}")
print("\nDeney kaydı tamamlandı.")
