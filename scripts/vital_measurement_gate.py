import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# -------------------------------------------------
# Final threshold ayarları
# -------------------------------------------------
DISPLAY_TH = 0.70
SUPPRESS_TH = 0.40

# -------------------------------------------------
# Dosyaları oku
# -------------------------------------------------
fusion = pd.read_csv("../results/enhanced_fusion_table.csv")
spo2 = pd.read_csv("../data/spo2_pr_log.csv")
imu = pd.read_csv("../data/imu_motion.csv")

# -------------------------------------------------
# Zaman eksenleri
# -------------------------------------------------
fusion["t"] = fusion["t"] - fusion["t"].iloc[0]
spo2["t"] = spo2["timestamp"] - spo2["timestamp"].iloc[0]
imu["t"] = imu["pc_time"] - imu["pc_time"].iloc[0]

# -------------------------------------------------
# IMU motion hesapla
# -------------------------------------------------
imu["motion"] = np.sqrt(
    imu["acc_x"]**2 +
    imu["acc_y"]**2 +
    imu["acc_z"]**2
)

baseline = imu["motion"].iloc[:min(200, len(imu))].mean()
imu["motion_dev"] = np.abs(imu["motion"] - baseline)
imu["motion_avg"] = imu["motion_dev"].rolling(40, min_periods=1).mean()

# Fusion zamanına taşı
fusion["motion_activity"] = np.interp(
    fusion["t"],
    imu["t"],
    imu["motion_avg"],
    left=imu["motion_avg"].iloc[0],
    right=imu["motion_avg"].iloc[-1]
)

# -------------------------------------------------
# SpO2 / PR'yi fusion zaman eksenine taşı
# -------------------------------------------------
fusion["spo2_interp"] = np.interp(
    fusion["t"],
    spo2["t"],
    spo2["spo2"],
    left=spo2["spo2"].iloc[0],
    right=spo2["spo2"].iloc[-1]
)

fusion["pr_interp"] = np.interp(
    fusion["t"],
    spo2["t"],
    spo2["pr"],
    left=spo2["pr"].iloc[0],
    right=spo2["pr"].iloc[-1]
)

# -------------------------------------------------
# Karar katmanı
# -------------------------------------------------
decisions = []
display_spo2 = []
display_pr = []

for _, row in fusion.iterrows():
    r = row["final_reliability"]
    spo2_val = row["spo2_interp"]
    pr_val = row["pr_interp"]

    if r > DISPLAY_TH:
        decision = "DISPLAY_MEASUREMENT"
        shown_spo2 = spo2_val
        shown_pr = pr_val
    elif r < SUPPRESS_TH:
        decision = "SUPPRESS_MEASUREMENT"
        shown_spo2 = np.nan
        shown_pr = np.nan
    else:
        decision = "WARNING_LOW_CONFIDENCE"
        shown_spo2 = spo2_val
        shown_pr = pr_val

    decisions.append(decision)
    display_spo2.append(shown_spo2)
    display_pr.append(shown_pr)

fusion["decision"] = decisions
fusion["display_spo2"] = display_spo2
fusion["display_pr"] = display_pr

# -------------------------------------------------
# Konsol özeti
# -------------------------------------------------
print("Decision thresholds:")
print(f"DISPLAY  > {DISPLAY_TH}")
print(f"SUPPRESS < {SUPPRESS_TH}")
print(f"WARNING  = [{SUPPRESS_TH}, {DISPLAY_TH}]")
print()

print("Decision counts:")
print(fusion["decision"].value_counts())
print()
print("Mean final reliability:", round(fusion["final_reliability"].mean(), 3))
print("Mean raw SpO2:", round(fusion["spo2_interp"].mean(), 2))
print("Mean raw PR:", round(fusion["pr_interp"].mean(), 2))
print("Mean motion activity:", round(fusion["motion_activity"].mean(), 2))

shown_spo2_mean = fusion["display_spo2"].mean()
shown_pr_mean = fusion["display_pr"].mean()

print("Mean displayed SpO2:", round(shown_spo2_mean, 2) if not np.isnan(shown_spo2_mean) else "Yok")
print("Mean displayed PR:", round(shown_pr_mean, 2) if not np.isnan(shown_pr_mean) else "Yok")

# -------------------------------------------------
# Kaydet
# -------------------------------------------------
fusion.to_csv("../results/vital_measurement_gate_table.csv", index=False)

# -------------------------------------------------
# Renk haritası
# -------------------------------------------------
color_map = {
    "DISPLAY_MEASUREMENT": "green",
    "WARNING_LOW_CONFIDENCE": "gold",
    "SUPPRESS_MEASUREMENT": "red"
}

# -------------------------------------------------
# Grafik
# -------------------------------------------------
fig, axes = plt.subplots(5, 1, figsize=(13, 13), sharex=True)

axes[0].plot(fusion["t"], fusion["ppg_raw"], linewidth=1.2)
axes[0].set_title("PPG Raw")
axes[0].set_ylabel("PPG")

axes[1].plot(fusion["t"], fusion["motion_activity"], color="purple", linewidth=1.5)
axes[1].set_title("Accelerometer Motion Activity")
axes[1].set_ylabel("Motion")

axes[2].plot(fusion["t"], fusion["final_reliability"], color="black", linewidth=2)
axes[2].set_title("Final Reliability")
axes[2].set_ylabel("Score")
axes[2].set_ylim(0, 1.05)

axes[3].plot(fusion["t"], fusion["spo2_interp"], label="Raw SpO2")
axes[3].plot(fusion["t"], fusion["display_spo2"], linewidth=2.5, label="Displayed SpO2")
axes[3].set_title("SpO2 Output Gate")
axes[3].set_ylabel("SpO2")
axes[3].legend()

axes[4].plot(fusion["t"], fusion["pr_interp"], label="Raw PR")
axes[4].plot(fusion["t"], fusion["display_pr"], linewidth=2.5, label="Displayed PR")
axes[4].set_title("Pulse Rate Output Gate")
axes[4].set_ylabel("PR")
axes[4].set_xlabel("Time (s)")
axes[4].legend()

# -------------------------------------------------
# Ardışık aynı kararları blok boya
# -------------------------------------------------
start_idx = 0
current_decision = fusion["decision"].iloc[0]

for i in range(1, len(fusion)):
    if fusion["decision"].iloc[i] != current_decision:
        t0 = fusion["t"].iloc[start_idx]
        t1 = fusion["t"].iloc[i - 1]
        c = color_map[current_decision]

        for ax in axes:
            ax.axvspan(t0, t1, alpha=0.16, color=c)

        start_idx = i
        current_decision = fusion["decision"].iloc[i]

# Son blok
t0 = fusion["t"].iloc[start_idx]
t1 = fusion["t"].iloc[len(fusion) - 1]
c = color_map[current_decision]
for ax in axes:
    ax.axvspan(t0, t1, alpha=0.16, color=c)

legend_patches = [
    Patch(color="green", alpha=0.35, label="DISPLAY_MEASUREMENT"),
    Patch(color="gold", alpha=0.35, label="WARNING_LOW_CONFIDENCE"),
    Patch(color="red", alpha=0.35, label="SUPPRESS_MEASUREMENT")
]
axes[0].legend(handles=legend_patches, loc="upper right")

plt.tight_layout()
plt.savefig("../results/vital_measurement_gate_with_motion.png", dpi=300)
plt.show()