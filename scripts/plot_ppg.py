import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/ppg_raw_static.csv")
df["t"] = df["timestamp"] - df["timestamp"].iloc[0]

plt.figure(figsize=(10,4))
plt.plot(df["t"], df["ppg_raw"])
plt.xlabel("Time (s)")
plt.ylabel("PPG Raw")
plt.title("OB1203 Raw PPG Signal")
plt.tight_layout()
plt.savefig("../results/plot_ppg_static.png", dpi=300)
plt.close()
