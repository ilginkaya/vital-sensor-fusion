import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../data/ppg_raw_motion.csv")

# zaman ekseni
df["t"] = df["timestamp"] - df["timestamp"].iloc[0]

# rolling DC (baseline)
window = 50
df["dc"] = df["ppg_raw"].rolling(window, min_periods=1).mean()

# AC component
df["ac"] = df["ppg_raw"] - df["dc"]

# Perfusion Index
df["pi"] = np.abs(df["ac"]) / df["dc"]

print("Ortalama PI:", df["pi"].mean())

plt.figure(figsize=(10,5))
plt.plot(df["t"], df["pi"])
plt.title("Perfusion Index (PPG Signal Quality)")
plt.xlabel("Time (s)")
plt.ylabel("PI")

plt.savefig("../results/perfusion_index.png", dpi=300)
plt.show()
