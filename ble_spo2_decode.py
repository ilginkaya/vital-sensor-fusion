import asyncio
from bleak import BleakClient

ADDRESS = "E35AC4A9-54FB-1B34-EB39-D9F040259BD3"
CHAR_UUID = "00002a5f-0000-1000-8000-00805f9b34fb"

def notification_handler(sender, data: bytearray):
    b = list(data)

    if len(b) < 5:
        return

    # Muhtemel little-endian decode
    spo2 = b[1] + (b[2] << 8)
    pulse = b[3] + (b[4] << 8)

    print(f"SpO2={spo2}  PR={pulse}  RAW={b[:10]}")

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Bağlandı:", client.is_connected)

        await client.start_notify(CHAR_UUID, notification_handler)
        print("Notify başladı. Parmağını sensöre koy ve 10 saniye bekle...")

        await asyncio.sleep(10)

        await client.stop_notify(CHAR_UUID)
        print("Notify durdu.")

asyncio.run(main())
