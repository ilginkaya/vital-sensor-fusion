import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Motion kayıt sonuçları
motion_df = pd.read_csv("../results/enhanced_fusion_table.csv")

# Static kayıt için basit reliability üretelim
static_ppg = pd.read_csv("../data/ppg_raw_static.csv")
static_ppg["t"] = static_ppg["timestamp"] - static_ppg["timestamp"].iloc[0]

# Static PPG quality
static_ppg["diff"] = static_ppg["ppg_raw"].diff().abs()
static_ppg["artifact"] = (
    (static_ppg["ppg_raw"] > 250000) |
    (static_ppg["ppg_raw"] < 10000) |
    (static_ppg["diff"] > 20000)
).astype(int)

static_ppg["ppg_quality"] = 1 - static_ppg["artifact"].rolling(20, min_periods=1).mean()

# Static motion yok kabul: score yüksek
static_ppg["motion_score"] = 0.95

# Static PI
static_ppg["dc"] = static_ppg["ppg_raw"].rolling(50, min_periods=1).mean()
static_ppg["ac"] = static_ppg["ppg_raw"] - static_ppg["dc"]
static_ppg["pi"] = np.abs(static_ppg["ac"]) / static_ppg["dc"]

pi_min = static_ppg["pi"].quantile(0.05)
pi_max = static_ppg["pi"].quantile(0.95)
static_ppg["pi_score"] = (static_ppg["pi"] - pi_min) / (pi_max - pi_min + 1e-9)
static_ppg["pi_score"] = static_ppg["pi_score"].clip(0, 1)

# Static BPM stability placeholder
static_ppg["bpm_stability"] = 0.85

# Static final reliability
static_ppg["final_reliability"] = (
    0.4 * static_ppg["ppg_quality"] +
    0.3 * static_ppg["motion_score"] +
    0.2 * static_ppg["pi_score"] +
    0.1 * static_ppg["bpm_stability"]
).clip(0, 1)

# Motion summary
motion_mean = motion_df["final_reliability"].mean()
static_mean = static_ppg["final_reliability"].mean()

print("Static mean reliability:", round(static_mean, 3))
print("Motion mean reliability:", round(motion_mean, 3))

# Grafik
plt.figure(figsize=(10, 6))

plt.subplot(2,1,1)
plt.plot(static_ppg["t"], static_ppg["final_reliability"], label="Static Reliability")
plt.ylim(0, 1.05)
plt.title("Static Recording Reliability")
plt.ylabel("Score")
plt.legend()

plt.subplot(2,1,2)
plt.plot(motion_df["t"], motion_df["final_reliability"], label="Motion Reliability")
plt.ylim(0, 1.05)
plt.title("Motion Recording Reliability")
plt.xlabel("Time (s)")
plt.ylabel("Score")
plt.legend()

plt.tight_layout()
plt.savefig("../results/static_vs_motion_reliability.png", dpi=300)
plt.show()

# küçük özet tablo
summary = pd.DataFrame({
    "Scenario": ["Static", "Motion"],
    "Mean_Reliability": [static_mean, motion_mean]
})
summary.to_csv("../results/static_vs_motion_summary.csv", index=False)
