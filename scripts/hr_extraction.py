import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

# -------------------------------------------------
# Veri oku
# -------------------------------------------------
df = pd.read_csv("../data/ppg_raw_motion.csv")
df["t"] = df["timestamp"] - df["timestamp"].iloc[0]

t = df["t"].to_numpy()
x = df["ppg_raw"].to_numpy()

# -------------------------------------------------
# Bandpass filter
# -------------------------------------------------
dt = np.mean(np.diff(t))
fs = 1 / dt

lowcut = 0.5   # Hz
highcut = 4.0  # Hz

low = lowcut / (fs / 2)
high = highcut / (fs / 2)

b, a = butter(3, [low, high], btype="band")
x_filt = filtfilt(b, a, x)

# -------------------------------------------------
# Peak detection
# -------------------------------------------------
peaks, props = find_peaks(
    x_filt,
    distance=fs * 0.6,                  # en az ~100 BPM üst sınır
    prominence=np.std(x_filt) * 0.3
)

peak_times = t[peaks]
peak_values = x_filt[peaks]

# -------------------------------------------------
# BPM hesaplama
# -------------------------------------------------
if len(peak_times) > 1:
    rr_intervals = np.diff(peak_times)           # saniye
    bpm_inst = 60 / rr_intervals                 # anlık BPM
    bpm_times = peak_times[1:]                   # her BPM ikinci peak'ten itibaren
    mean_bpm = np.mean(bpm_inst)
    bpm_std = np.std(bpm_inst)
else:
    rr_intervals = np.array([])
    bpm_inst = np.array([])
    bpm_times = np.array([])
    mean_bpm = np.nan
    bpm_std = np.nan

print("Toplam peak sayısı:", len(peaks))
print("Ortalama BPM:", round(mean_bpm, 2) if not np.isnan(mean_bpm) else "Hesaplanamadı")
print("BPM std:", round(bpm_std, 2) if not np.isnan(bpm_std) else "Hesaplanamadı")

# -------------------------------------------------
# BPM stability score
# düşük std = daha stabil
# -------------------------------------------------
if len(bpm_inst) > 2:
    bpm_df = pd.DataFrame({"t": bpm_times, "bpm": bpm_inst})
    bpm_df["bpm_std_roll"] = bpm_df["bpm"].rolling(5, min_periods=1).std().fillna(0)

    max_std = max(bpm_df["bpm_std_roll"].quantile(0.95), 1e-6)
    bpm_df["bpm_stability"] = 1 - (bpm_df["bpm_std_roll"] / max_std)
    bpm_df["bpm_stability"] = bpm_df["bpm_stability"].clip(0, 1)

    mean_bpm_stability = bpm_df["bpm_stability"].mean()
else:
    bpm_df = pd.DataFrame(columns=["t", "bpm", "bpm_std_roll", "bpm_stability"])
    mean_bpm_stability = np.nan

print("Ortalama BPM stability:", round(mean_bpm_stability, 3) if not np.isnan(mean_bpm_stability) else "Hesaplanamadı")

# -------------------------------------------------
# Sonuçları kaydet
# -------------------------------------------------
if len(bpm_df) > 0:
    bpm_df.to_csv("../results/hr_bpm_series.csv", index=False)

# -------------------------------------------------
# Grafik
# -------------------------------------------------
plt.figure(figsize=(12, 8))

plt.subplot(3,1,1)
plt.plot(t, x, label="Raw PPG")
plt.title("Raw PPG Signal")
plt.ylabel("PPG")

plt.subplot(3,1,2)
plt.plot(t, x_filt, label="Filtered PPG")
plt.scatter(peak_times, peak_values, s=25, label="Detected Peaks")
plt.title("Filtered PPG with Peaks")
plt.ylabel("Filtered")
plt.legend()

plt.subplot(3,1,3)
if len(bpm_inst) > 0:
    plt.plot(bpm_times, bpm_inst, marker="o", label="Instant BPM")
    plt.axhline(mean_bpm, linestyle="--", label=f"Mean BPM = {mean_bpm:.1f}")
plt.title("Instant Heart Rate")
plt.xlabel("Time (s)")
plt.ylabel("BPM")
plt.legend()

plt.tight_layout()
plt.savefig("../results/hr_extraction.png", dpi=300)
plt.show()
