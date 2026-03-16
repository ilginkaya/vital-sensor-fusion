import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

df = pd.read_csv("../data/ppg_raw_static.csv")

t = df["timestamp"] - df["timestamp"].iloc[0]
ppg = df["ppg_raw"]

dt = np.mean(np.diff(t))
fs = 1 / dt

df["diff"] = df["ppg_raw"].diff().abs()
df["artifact"] = (
    (df["ppg_raw"] > 250000) |
    (df["ppg_raw"] < 10000) |
    (df["diff"] > 20000)
).astype(int)

window = 20
df["reliability"] = 1 - df["artifact"].rolling(window).mean()
reliability_mean = df["reliability"].mean()

low = 0.5 / (fs / 2)
high = 4.0 / (fs / 2)
b, a = butter(3, [low, high], btype="band")
ppg_filtered = filtfilt(b, a, ppg)

peaks, _ = find_peaks(
    ppg_filtered,
    distance=fs * 0.7,
    prominence=80,
    height=40
)

peak_times = t.iloc[peaks].to_numpy()
intervals = np.diff(peak_times)

if len(intervals) > 0:
    bpm = 60 / np.mean(intervals)
else:
    bpm = None

threshold = 0.6

if bpm is not None and reliability_mean > threshold:
    status = f"VALID BPM: {round(bpm,2)}"
else:
    status = "INVALID BPM (low reliability)"

plt.figure(figsize=(12, 8))

plt.subplot(3,1,1)
plt.plot(t, ppg)
plt.title("Raw PPG")

plt.subplot(3,1,2)
plt.plot(t, df["reliability"])
plt.axhline(threshold, linestyle="--")
plt.title("Signal Reliability Score")
plt.ylim(0, 1)

plt.subplot(3,1,3)
plt.plot(t, ppg_filtered, label="Filtered PPG")
if bpm is not None and reliability_mean > threshold:
    plt.scatter(t.iloc[peaks], ppg_filtered[peaks], s=30, label="Peaks")
plt.title(status)
plt.legend()

plt.tight_layout()
plt.savefig("../results/signal_quality_gate_static.png", dpi=300)
plt.close()
