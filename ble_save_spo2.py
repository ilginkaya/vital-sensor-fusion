import asyncio
import csv
import time
from bleak import BleakClient

ADDRESS = "E35AC4A9-54FB-1B34-EB39-D9F040259BD3"
CHAR_UUID = "00002a5f-0000-1000-8000-00805f9b34fb"
OUTPUT = "data/spo2_pr_log.csv"

rows = []

def notification_handler(sender, data: bytearray):
    b = list(data)

    if len(b) < 5:
        return

    # Little-endian decode
    spo2 = b[1] + (b[2] << 8)
    pr = b[3] + (b[4] << 8)

    # Geçersiz ölçümleri at
    if spo2 == 0 or pr == 0:
        return

    ts = time.time()
    rows.append([ts, spo2, pr])

    print(f"{ts:.3f}, SpO2={spo2}, PR={pr}")

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Bağlandı:", client.is_connected)
        print("10 saniye kayıt alınıyor... Parmağını sensörde sabit tut.")

        await client.start_notify(CHAR_UUID, notification_handler)
        await asyncio.sleep(30)
        await client.stop_notify(CHAR_UUID)

    with open(OUTPUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "spo2", "pr"])
        writer.writerows(rows)

    print(f"Kayıt tamamlandı. {len(rows)} örnek {OUTPUT} dosyasına yazıldı.")

asyncio.run(main())
