import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# Enhanced fusion sonuçlarını oku
df = pd.read_csv("../results/enhanced_fusion_table.csv")

# Karar kuralları
decisions = []
for _, row in df.iterrows():
    r = row["final_reliability"]

    if r > 0.7:
        decisions.append("DISPLAY_MEASUREMENT")
    elif r < 0.4:
        decisions.append("SUPPRESS_MEASUREMENT")
    else:
        decisions.append("WARNING_LOW_CONFIDENCE")

df["decision"] = decisions

print("Decision counts:")
print(df["decision"].value_counts())
print()
print("Mean final reliability:", round(df["final_reliability"].mean(), 3))

# Kaydet
df.to_csv("../results/decision_layer_table.csv", index=False)

# Renk haritası
color_map = {
    "DISPLAY_MEASUREMENT": "green",
    "WARNING_LOW_CONFIDENCE": "gold",
    "SUPPRESS_MEASUREMENT": "red"
}

# Grafik
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

axes[0].plot(df["t"], df["ppg_raw"], linewidth=1.5)
axes[0].set_title("PPG Raw with Decision Layer")
axes[0].set_ylabel("PPG")

axes[1].plot(df["t"], df["final_reliability"], color="black", linewidth=2)
axes[1].set_title("Final Reliability")
axes[1].set_ylabel("Score")
axes[1].set_xlabel("Time (s)")
axes[1].set_ylim(0, 1.05)

# Ardışık aynı kararları blok halinde boya
start_idx = 0
current_decision = df["decision"].iloc[0]

for i in range(1, len(df)):
    if df["decision"].iloc[i] != current_decision:
        t0 = df["t"].iloc[start_idx]
        t1 = df["t"].iloc[i - 1]
        c = color_map[current_decision]

        axes[0].axvspan(t0, t1, alpha=0.22, color=c)
        axes[1].axvspan(t0, t1, alpha=0.22, color=c)

        start_idx = i
        current_decision = df["decision"].iloc[i]

# Son blok
t0 = df["t"].iloc[start_idx]
t1 = df["t"].iloc[len(df) - 1]
c = color_map[current_decision]
axes[0].axvspan(t0, t1, alpha=0.22, color=c)
axes[1].axvspan(t0, t1, alpha=0.22, color=c)

legend_patches = [
    Patch(color="green", alpha=0.4, label="DISPLAY_MEASUREMENT"),
    Patch(color="gold", alpha=0.4, label="WARNING_LOW_CONFIDENCE"),
    Patch(color="red", alpha=0.4, label="SUPPRESS_MEASUREMENT")
]
axes[0].legend(handles=legend_patches, loc="upper right")

plt.tight_layout()
plt.savefig("../results/decision_layer_overlay.png", dpi=300)
plt.show()
