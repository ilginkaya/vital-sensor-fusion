import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/ppg_raw_motion.csv")
df["t"] = df["timestamp"] - df["timestamp"].iloc[0]

df["diff"] = df["ppg_raw"].diff().abs()
df["artifact"] = (
    (df["ppg_raw"] > 250000) |
    (df["ppg_raw"] < 10000) |
    (df["diff"] > 20000)
).astype(int)

window = 20
df["reliability"] = 1 - df["artifact"].rolling(window).mean()

plt.figure(figsize=(12,6))

plt.subplot(2,1,1)
plt.plot(df["t"], df["ppg_raw"])
plt.title("PPG Raw Signal")
plt.ylabel("PPG")

plt.subplot(2,1,2)
plt.plot(df["t"], df["reliability"])
plt.ylim(0,1)
plt.title("Signal Reliability Score")
plt.ylabel("Reliability")
plt.xlabel("Time (s)")

plt.tight_layout()
plt.savefig("../results/reliability_score_motion.png", dpi=300)
plt.close()
