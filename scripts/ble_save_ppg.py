import asyncio
import csv
import time
from bleak import BleakClient

ADDRESS = "E35AC4A9-54FB-1B34-EB39-D9F040259BD3"
CHAR_UUID = "00002a5f-0000-1000-8000-00805f9b34fb"

rows = []

def u24_le(b0, b1, b2):
    return b0 | (b1 << 8) | (b2 << 16)

def notification_handler(sender, data):
    packet = list(data)
    ts = time.time()

    if len(packet) >= 10:
        ppg_raw = u24_le(packet[7], packet[8], packet[9])
        rows.append([ts, ppg_raw])
        print(f"{ts:.3f}, {ppg_raw}")

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Bağlandı:", client.is_connected)
        await client.start_notify(CHAR_UUID, notification_handler)
        print("20 saniye kayıt alınıyor... Parmağını sensörde tut.")
        await asyncio.sleep(20)
        await client.stop_notify(CHAR_UUID)

    with open("ppg_raw.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "ppg_raw"])
        writer.writerows(rows)

    print(f"Kayıt tamamlandı. {len(rows)} örnek ppg_raw.csv dosyasına yazıldı.")

asyncio.run(main())
