# VitalSense: Sensor Fusion for Motion-Robust Vital Sign Monitoring 🏥🚀

VitalSense is an R&D prototype designed to solve the **"Alarm Fatigue"** problem in wearable healthcare devices. By leveraging **Sensor Fusion** techniques, it distinguishes between actual physiological changes and **Motion Artifacts (MA)** to ensure reliable heart rate and SpO₂ monitoring.

## 📋 Table of Contents
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [System Architecture](#system-architecture)
- [Features](#features)
- [Hardware Stack](#hardware-stack)
- [Live Demo](#-live-demo)

---

## 🔍 The Problem
PPG (Photoplethysmography) sensors are highly sensitive to movement. In clinical settings, simple patient movements (like drinking water or adjusting bed position) cause signal distortions, leading to:
- **False Alarms:** Unnecessary alerts that distract medical staff.
- **Alarm Fatigue:** Reduced responsiveness of clinicians to real emergencies due to excessive false alerts.

## 💡 The Solution: Reliability-Aware Monitoring
VitalSense doesn't just display data; it questions its **validity**. By fusing PPG data with Accelerometer (IMU) data, the system calculates a **Signal Reliability Score (0.0 - 1.0)** and decides whether to display or suppress the measurement.

---

## 🏗 System Architecture

The project follows a modular signal processing pipeline:

1.  **Data Acquisition:** Real-time streaming from Renesas (PPG) and TI SensorTag (IMU).
2. **Preprocessing**
   - **PPG:** 0.5–4 Hz band-pass filtering to remove high-frequency noise and baseline wander  
   - **IMU:** Rolling average for motion stabilization
3.  **Feature Extraction:** Peak detection for HR/BPM and Magnitude calculation for motion.
4.  **Sensor Fusion Layer:** Calculation of the *Signal Reliability Score* based on PI (Perfusion Index) and Motion Magnitude.
5.  **Decision Layer:**
    - 🟢 **DISPLAY:** High confidence, reliable data.
    - 🟡 **WARNING:** Medium confidence, proceed with caution.
    - 🔴 **SUPPRESS:** High motion detected, false alarm prevented.

---

## ✨ Features
- **Real-time Dashboard:** Built with a modern UI to monitor raw PPG, motion trends, and reliability scores.
- **Firebase Integration:** Real-time data synchronization for remote patient monitoring (IoMT).
- **Hysteresis & Windowing:** Prevents "flickering" of the UI by smoothing decision transitions.
- **Motion Robustness:** Specifically tuned to handle typical daily movement artifacts.

## 🛠 Hardware Stack
- **Vital Sensor:** Renesas Electronics OB1203 (Heart Rate, SpO₂, Raw PPG).
- **Motion Sensor:** Texas Instruments CC2650 SensorTag (3-axis Accelerometer).
- **Connectivity:** Bluetooth Low Energy (BLE).

---

## 📸 Dashboard Preview
<img width="1416" height="770" alt="Ekran Resmi 2026-03-16 18 02 56" src="https://github.com/user-attachments/assets/887edf4e-832b-4e6a-b619-90cc3be10104" />


---<img width="1420" height="775" alt="Ekran Resmi 2026-03-16 18 03 21" src="https://github.com/user-attachments/assets/45e648e6-b520-4337-bdf0-f95f127e18cc" />


## 🚀 Live Demo

You can explore the real-time monitoring dashboard here:

👉 https://vital-sensor-fusion.web.app

The dashboard visualizes:

- Raw PPG signal
- Motion activity
- SpO₂ trend
- Pulse rate trend
- Reliability score
- Decision layer (Display / Warning / Suppress)

This demonstrates how the system reacts to motion artifacts and gradually restores measurement confidence.
