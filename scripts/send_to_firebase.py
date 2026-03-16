import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import numpy as np
import time

cred = credentials.Certificate("../vital-sensor-fusion-firebase-adminsdk-fbsvc-f3970896c5.json")

try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://vital-sensor-fusion-default-rtdb.europe-west1.firebasedatabase.app"
    })

ref = db.reference("vitals")

spo2 = pd.read_csv("../data/spo2_pr_log1.csv")
imu = pd.read_csv("../data/imu_motion1.csv")
ppg = pd.read_csv("../data/ppg_raw_motion1.csv")

# PPG kolonunu bul
possible_ppg_cols = ["ppg", "ppg_raw", "value", "sample"]
ppg_col = None
for col in possible_ppg_cols:
    if col in ppg.columns:
        ppg_col = col
        break

if ppg_col is None:
    # ilk sayısal kolonu kullan
    numeric_cols = ppg.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        raise ValueError("PPG dosyasında uygun sayısal kolon bulunamadı.")
    ppg_col = numeric_cols[-1]

def compute_motion(ax, ay, az):
    return float(np.sqrt(ax * ax + ay * ay + az * az))

def compute_reliability(spo2_val, pr_val, motion_val):
    score = 1.0

    if motion_val > 1800:
        score -= 0.45
    elif motion_val > 1500:
        score -= 0.30
    elif motion_val > 1300:
        score -= 0.20
    elif motion_val > 1100:
        score -= 0.10

    if spo2_val < 95:
        score -= 0.10

    if pr_val < 55 or pr_val > 120:
        score -= 0.12

    return max(0.0, min(1.0, score))

def get_decision(reliability):
    if reliability > 0.75:
        return "DISPLAY"
    elif reliability < 0.40:
        return "SUPPRESS"
    return "WARNING"

n = min(len(spo2), len(imu), len(ppg))

for i in range(n):
    spo2_val = float(spo2["spo2"].iloc[i])
    pr_val = float(spo2["pr"].iloc[i])

    ax = float(imu["acc_x"].iloc[i])
    ay = float(imu["acc_y"].iloc[i])
    az = float(imu["acc_z"].iloc[i])

    ppg_val = float(ppg[ppg_col].iloc[i])

    motion_val = compute_motion(ax, ay, az)
    reliability_val = compute_reliability(spo2_val, pr_val, motion_val)
    decision_val = get_decision(reliability_val)

    data = {
        "spo2": spo2_val,
        "pulse_rate": pr_val,
        "ppg_raw": ppg_val,
        "acc_x": ax,
        "acc_y": ay,
        "acc_z": az,
        "motion": motion_val,
        "reliability": reliability_val,
        "decision": decision_val,
        "timestamp": time.time()
    }

    ref.push(data)
    print("Gönderildi:", data)
    time.sleep(1)
