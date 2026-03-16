import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Dosyaları oku
ppg = pd.read_csv("../data/ppg_raw_motion.csv")
imu = pd.read_csv("../data/imu_motion.csv")

# Zaman ekseni oluştur
ppg["t"] = ppg["timestamp"] - ppg["timestamp"].iloc[0]
imu["t"] = imu["pc_time"] - imu["pc_time"].iloc[0]

# -------------------
# PPG reliability
# -------------------
ppg["diff"] = ppg["ppg_raw"].diff().abs()

ppg["artifact"] = (
    (ppg["ppg_raw"] > 250000) |
    (ppg["ppg_raw"] < 10000) |
    (ppg["diff"] > 20000)
).astype(int)

window_ppg = 20
ppg["ppg_reliability"] = 1 - ppg["artifact"].rolling(window_ppg, min_periods=1).mean()

# -------------------
# IMU motion score
# -------------------
imu["motion"] = np.sqrt(
    imu["acc_x"]**2 +
    imu["acc_y"]**2 +
    imu["acc_z"]**2
)

baseline = imu["motion"].iloc[:200].mean()
imu["motion_dev"] = np.abs(imu["motion"] - baseline)

# normalize et
max_dev = imu["motion_dev"].max()
if max_dev == 0:
    imu["motion_score"] = 1.0
else:
    imu["motion_score"] = 1 - (imu["motion_dev"] / max_dev)

imu["motion_score"] = imu["motion_score"].clip(0, 1)

# biraz yumuşat
imu["motion_score_smooth"] = imu["motion_score"].rolling(30, min_periods=1).mean()

# -------------------
# Aynı örnek sayısına getir
# -------------------
imu_resampled = np.interp(
    ppg["t"],
    imu["t"],
    imu["motion_score_smooth"]
)

ppg["motion_score"] = imu_resampled

# -------------------
# Final fusion reliability
# -------------------
ppg["final_reliability"] = ppg["ppg_reliability"] * ppg["motion_score"]

# -------------------
# Grafik
# -------------------
plt.figure(figsize=(12, 8))

plt.subplot(3,1,1)
plt.plot(ppg["t"], ppg["ppg_raw"])
plt.title("PPG Raw (Motion Recording)")
plt.ylabel("PPG")

plt.subplot(3,1,2)
plt.plot(imu["t"], imu["motion"], label="Motion Magnitude")
plt.title("IMU Motion")
plt.ylabel("Motion")

plt.subplot(3,1,3)
plt.plot(ppg["t"], ppg["ppg_reliability"], label="PPG Reliability")
plt.plot(ppg["t"], ppg["motion_score"], label="Motion Score")
plt.plot(ppg["t"], ppg["final_reliability"], label="Final Fusion Reliability", linewidth=2)
plt.title("Sensor Fusion Reliability")
plt.xlabel("Time (s)")
plt.ylabel("Score")
plt.ylim(0, 1.05)
plt.legend()

plt.tight_layout()
plt.savefig("../results/fusion_reliability.png", dpi=300)
plt.show()

print("Ortalama PPG reliability:", round(ppg["ppg_reliability"].mean(), 3))
print("Ortalama motion score:", round(ppg["motion_score"].mean(), 3))
print("Ortalama final reliability:", round(ppg["final_reliability"].mean(), 3))
