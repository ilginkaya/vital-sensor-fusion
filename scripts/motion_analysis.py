import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# IMU verisini oku
df = pd.read_csv("../data/imu_motion.csv")

# Motion magnitude hesapla
df["motion"] = np.sqrt(
    df["acc_x"]**2 +
    df["acc_y"]**2 +
    df["acc_z"]**2
)

print("Ortalama motion:", df["motion"].mean())

# Grafik çiz
plt.figure(figsize=(10,5))
plt.plot(df["motion"])
plt.title("IMU Motion Magnitude")
plt.xlabel("Sample")
plt.ylabel("Motion Level")

plt.savefig("../results/motion_plot.png")

plt.show()
