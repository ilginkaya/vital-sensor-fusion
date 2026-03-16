import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

# CSV oku
df = pd.read_csv("ppg_raw_static.csv")

# zaman vektörü
t = df["timestamp"] - df["timestamp"].iloc[0]
ppg = df["ppg_raw"]

# örnekleme frekansı
dt = np.mean(np.diff(t))
fs = 1 / dt
print(f"Tahmini örnekleme frekansı: {fs:.2f} Hz")

# bandpass filtre (PPG için tipik aralık)
low = 0.5 / (fs/2)
high = 4.0 / (fs/2)
b, a = butter(3, [low, high], btype="band")

ppg_filtered = filtfilt(b, a, ppg)

# peak tespiti (daha sağlam)
peaks, properties = find_peaks(
    ppg_filtered,
    distance = fs * 0.7,      # iki kalp atımı arası min süre
    prominence = 80,          # küçük gürültü tepelerini ele
    height = 40               # minimum tepe yüksekliği
)

# BPM hesaplama
peak_times = t.iloc[peaks].to_numpy()
intervals = np.diff(peak_times)

if len(intervals) > 0:
    mean_interval = np.mean(intervals)
    bpm = 60 / mean_interval
    print("Tahmini Kalp Hızı:", round(bpm,2), "BPM")
else:
    print("Yeterli peak bulunamadı")

# grafikler
plt.figure(figsize=(12,8))

plt.subplot(3,1,1)
plt.plot(t, ppg)
plt.title("Raw PPG")

plt.subplot(3,1,2)
plt.plot(t, ppg_filtered)
plt.title("Filtered PPG")

plt.subplot(3,1,3)
plt.plot(t, ppg_filtered, label="Filtered PPG")
plt.scatter(t.iloc[peaks], ppg_filtered[peaks], s=30, label="Peaks")
plt.title("PPG Peaks (Heart Beats)")
plt.legend()

plt.tight_layout()
plt.show()
