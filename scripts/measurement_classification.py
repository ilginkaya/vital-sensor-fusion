import pandas as pd
import numpy as np

ppg = pd.read_csv("../data/ppg_raw_motion.csv")
imu = pd.read_csv("../data/imu_motion.csv")

imu["motion"] = np.sqrt(
    imu["acc_x"]**2 +
    imu["acc_y"]**2 +
    imu["acc_z"]**2
)

baseline = imu["motion"].iloc[:200].mean()
imu["motion_dev"] = np.abs(imu["motion"] - baseline)

motion_threshold = imu["motion_dev"].mean()

ppg["diff"] = ppg["ppg_raw"].diff().abs()
ppg_bad = ppg["diff"] > 20000

labels = []

for i in range(len(ppg)):
    motion = imu["motion_dev"].iloc[min(i, len(imu)-1)]
    bad = ppg_bad.iloc[i]

    if motion < motion_threshold and not bad:
        labels.append("VALID")

    elif motion > motion_threshold and bad:
        labels.append("MOTION_ARTIFACT")

    else:
        labels.append("POSSIBLE_PHYS_CHANGE")

ppg["classification"] = labels

print(ppg["classification"].value_counts())

ppg.to_csv("../results/measurement_classification.csv", index=False)
