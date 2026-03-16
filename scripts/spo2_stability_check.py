import pandas as pd

# Dosyayı oku
df = pd.read_csv("../data/spo2_pr_log.csv")

# Zaman ekseni
df["t"] = df["timestamp"] - df["timestamp"].iloc[0]

# İlk 5 saniyeyi at
df_valid = df[df["t"] >= 5].copy()

if len(df_valid) == 0:
    print("5. saniyeden sonra veri kalmadı. Daha uzun kayıt al.")
    exit()

# İstatistikler
spo2_mean = df_valid["spo2"].mean()
spo2_std = df_valid["spo2"].std()
pr_mean = df_valid["pr"].mean()
pr_std = df_valid["pr"].std()

print("Analiz edilen örnek sayısı:", len(df_valid))
print("Ortalama SpO2:", round(spo2_mean, 2))
print("SpO2 std:", round(spo2_std, 2))
print("Ortalama PR:", round(pr_mean, 2))
print("PR std:", round(pr_std, 2))

# Basit yorum
stable = True
reasons = []

if spo2_mean < 90:
    stable = False
    reasons.append("SpO2 ortalaması çok düşük")

if spo2_std > 2:
    stable = False
    reasons.append("SpO2 çok dalgalı")

if pr_std > 8:
    stable = False
    reasons.append("PR çok dalgalı")

print()

if stable:
    print("Sonuç: ÖLÇÜM GÖRECE STABİL")
else:
    print("Sonuç: ÖLÇÜM ŞÜPHELİ / DÜŞÜK GÜVEN")
    print("Nedenler:")
    for r in reasons:
        print("-", r)
