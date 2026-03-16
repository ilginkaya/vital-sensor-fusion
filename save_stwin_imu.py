import serial
import csv
import re
import time

PORT = "/dev/tty.usbmodem00000000001A1"
BAUD = 115200
OUTPUT = "data/imu_motion.csv"

ts_pattern = re.compile(r"TimeStamp:\s*(\d+)")
acc_pattern = re.compile(r"Acc_X:\s*(-?\d+),\s*Acc_Y:\s*(-?\d+),\s*Acc_Z\s*:(-?\d+)")

current_ts = None

with serial.Serial(PORT, BAUD, timeout=1) as ser, open(OUTPUT, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["pc_time", "device_timestamp", "acc_x", "acc_y", "acc_z"])

    print("IMU kaydı başladı... Durdurmak için Ctrl+C")

    try:
        while True:
            line = ser.readline().decode(errors="ignore").strip()

            if not line:
                continue

            print(line)

            ts_match = ts_pattern.search(line)
            if ts_match:
                current_ts = int(ts_match.group(1))

            acc_match = acc_pattern.search(line)
            if acc_match:
                acc_x = int(acc_match.group(1))
                acc_y = int(acc_match.group(2))
                acc_z = int(acc_match.group(3))

                writer.writerow([time.time(), current_ts, acc_x, acc_y, acc_z])
                f.flush()

    except KeyboardInterrupt:
        print("\nIMU kaydı durduruldu.")
