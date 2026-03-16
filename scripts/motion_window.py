import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("../data/imu_motion.csv")

df["motion"] = np.sqrt(
    df["acc_x"]**2 +
    df["acc_y"]**2 +
    df["acc_z"]**2
)

baseline = df["motion"].iloc[:200].mean()
df["motion_dev"] = np.abs(df["motion"] - baseline)

# 2 saniyelik hareket ortalaması
window = 40
df["motion_avg"] = df["motion_dev"].rolling(window, min_periods=1).mean()

plt.figure(figsize=(10,5))
plt.plot(df["motion_avg"])
plt.title("Rolling Motion Activity")
plt.xlabel("Sample")
plt.ylabel("Motion Activity")

plt.savefig("../results/motion_activity.png", dpi=300)
plt.show()
