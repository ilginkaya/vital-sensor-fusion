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

plt.figure(figsize=(12,5))
plt.plot(df["t"], df["ppg_raw"], label="PPG Raw")
plt.scatter(
    df[df["artifact"] == 1]["t"],
    df[df["artifact"] == 1]["ppg_raw"],
    label="Artifact",
    s=20
)
plt.xlabel("Time (s)")
plt.ylabel("PPG Raw")
plt.title("Motion Artifact Detection on PPG Signal")
plt.legend()
plt.tight_layout()
plt.savefig("../results/detect_artifact_motion.png", dpi=300)
plt.close()
