import os

print("PPG analiz pipeline başlıyor...\n")

data_file = "../data/ppg_raw_static.csv"

print("1) PPG grafiği oluşturuluyor...")
os.system(f"python3 ./plot_ppg.py {data_file}")

print("2) Artefakt analizi yapılıyor...")
os.system(f"python3 ./detect_artifact.py {data_file}")

print("3) Signal quality gate çalışıyor...")
os.system(f"python3 ./signal_quality_gate.py {data_file}")

print("4) Reliability score hesaplanıyor...")
os.system(f"python3 ./reliability_score.py {data_file}")

print("\nTüm analizler tamamlandı.")