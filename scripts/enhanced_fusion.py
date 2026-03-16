import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks

# -------------------------
# Dosyaları oku
# -------------------------
ppg = pd.read_csv("../data/ppg_raw_motion.csv")
imu = pd.read_csv("../data/imu_motion.csv")

ppg["t"] = ppg["timestamp"] - ppg["timestamp"].iloc[0]
imu["t"] = imu["pc_time"] - imu["pc_time"].iloc[0]

# -------------------------
# 1) PPG quality
# -------------------------
ppg["diff"] = ppg["ppg_raw"].diff().abs()
ppg["artifact"] = (
    (ppg["ppg_raw"] > 250000) |
    (ppg["ppg_raw"] < 10000) |
    (ppg["diff"] > 20000)
).astype(int)

ppg["ppg_quality"] = 1 - ppg["artifact"].rolling(20, min_periods=1).mean()

# -------------------------
# 2) Perfusion Index (PI)
# -------------------------
ppg["dc"] = ppg["ppg_raw"].rolling(50, min_periods=1).mean()
ppg["ac"] = ppg["ppg_raw"] - ppg["dc"]
ppg["pi"] = np.abs(ppg["ac"]) / ppg["dc"]

# normalize PI to 0-1
pi_min = ppg["pi"].quantile(0.05)
pi_max = ppg["pi"].quantile(0.95)
ppg["pi_score"] = (ppg["pi"] - pi_min) / (pi_max - pi_min + 1e-9)
ppg["pi_score"] = ppg["pi_score"].clip(0, 1)

# -------------------------
# 3) BPM stability
# -------------------------
t = ppg["t"].to_numpy()
x = ppg["ppg_raw"].to_numpy()

dt = np.mean(np.diff(t))
fs = 1 / dt

low = 0.5 / (fs / 2)
high = 4.0 / (fs / 2)
b, a = butter(3, [low, high], btype="band")
x_filt = filtfilt(b, a, x)

peaks, _ = find_peaks(
    x_filt,
    distance=fs * 0.6,
    prominence=np.std(x_filt) * 0.3
)

peak_times = t[peaks]

if len(peak_times) > 2:
    rr = np.diff(peak_times)
    bpm_inst = 60 / rr
    bpm_t = peak_times[1:]

    bpm_df = pd.DataFrame({"t": bpm_t, "bpm": bpm_inst})
    bpm_df["bpm_std"] = bpm_df["bpm"].rolling(5, min_periods=1).std().fillna(0)

    # düşük std = iyi
    std_max = max(bpm_df["bpm_std"].quantile(0.95), 1e-6)
    bpm_df["bpm_stability"] = 1 - (bpm_df["bpm_std"] / std_max)
    bpm_df["bpm_stability"] = bpm_df["bpm_stability"].clip(0, 1)

    ppg["bpm_stability"] = np.interp(
        ppg["t"], bpm_df["t"], bpm_df["bpm_stability"],
        left=bpm_df["bpm_stability"].iloc[0],
        right=bpm_df["bpm_stability"].iloc[-1]
    )
else:
    ppg["bpm_stability"] = 0.5

# -------------------------
# 4) Motion score
# -------------------------
imu["motion"] = np.sqrt(
    imu["acc_x"]**2 +
    imu["acc_y"]**2 +
    imu["acc_z"]**2
)

baseline = imu["motion"].iloc[:min(200, len(imu))].mean()
imu["motion_dev"] = np.abs(imu["motion"] - baseline)
imu["motion_avg"] = imu["motion_dev"].rolling(40, min_periods=1).mean()

motion_max = max(imu["motion_avg"].quantile(0.95), 1e-6)
imu["motion_score"] = 1 - (imu["motion_avg"] / motion_max)
imu["motion_score"] = imu["motion_score"].clip(0, 1)

ppg["motion_score"] = np.interp(
    ppg["t"], imu["t"], imu["motion_score"],
    left=imu["motion_score"].iloc[0],
    right=imu["motion_score"].iloc[-1]
)

# -------------------------
# 5) Enhanced fusion score
# -------------------------
ppg["final_reliability"] = (
    0.4 * ppg["ppg_quality"] +
    0.3 * ppg["motion_score"] +
    0.2 * ppg["pi_score"] +
    0.1 * ppg["bpm_stability"]
)

ppg["final_reliability"] = ppg["final_reliability"].clip(0, 1)

# -------------------------
# 6) Classification
# -------------------------
labels = []
for _, row in ppg.iterrows():
    if row["motion_score"] < 0.55 and row["ppg_quality"] < 0.55:
        labels.append("MOTION_ARTIFACT")
    elif row["final_reliability"] > 0.7:
        labels.append("VALID")
    else:
        labels.append("POSSIBLE_PHYS_CHANGE")

ppg["classification"] = labels

print("Classification counts:")
print(ppg["classification"].value_counts())
print()
print("Mean PPG quality:", round(ppg["ppg_quality"].mean(), 3))
print("Mean motion score:", round(ppg["motion_score"].mean(), 3))
print("Mean PI score:", round(ppg["pi_score"].mean(), 3))
print("Mean BPM stability:", round(ppg["bpm_stability"].mean(), 3))
print("Mean final reliability:", round(ppg["final_reliability"].mean(), 3))

# -------------------------
# 7) Grafik
# -------------------------
plt.figure(figsize=(12, 10))

plt.subplot(4,1,1)
plt.plot(ppg["t"], ppg["ppg_raw"])
plt.title("PPG Raw")
plt.ylabel("PPG")

plt.subplot(4,1,2)
plt.plot(imu["t"], imu["motion_avg"])
plt.title("Rolling Motion Activity")
plt.ylabel("Motion")

plt.subplot(4,1,3)
plt.plot(ppg["t"], ppg["ppg_quality"], label="PPG Quality")
plt.plot(ppg["t"], ppg["motion_score"], label="Motion Score")
plt.plot(ppg["t"], ppg["pi_score"], label="PI Score")
plt.plot(ppg["t"], ppg["bpm_stability"], label="BPM Stability")
plt.ylim(0, 1.05)
plt.title("Component Scores")
plt.legend()

plt.subplot(4,1,4)
plt.plot(ppg["t"], ppg["final_reliability"], color="black", label="Final Reliability")
plt.ylim(0, 1.05)
plt.title("Enhanced Fusion Reliability")
plt.xlabel("Time (s)")
plt.ylabel("Score")
plt.legend()

plt.tight_layout()
plt.savefig("../results/enhanced_fusion.png", dpi=300)
plt.show()

ppg.to_csv("../results/enhanced_fusion_table.csv", index=False)
