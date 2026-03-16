import asyncio
from bleak import BleakClient

ADDRESS = "32CD2B95-DE67-D928-2653-98CFAB39DB49"

CHARS = [
    "6e400003-b5a3-f393-e0a9-e50e24dcca9e",
    "f0002413-0451-4000-b000-000000000000",
    "f0002415-0451-4000-b000-000000000000",
    "f0002513-0451-4000-b000-000000000000",
]

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Bağlandı:", client.is_connected)

        for char_uuid in CHARS:
            try:
                data = await client.read_gatt_char(char_uuid)
                print(f"\nCHAR: {char_uuid}")
                print("HEX :", data.hex())
                print("LIST:", list(data))
            except Exception as e:
                print(f"\nCHAR: {char_uuid}")
                print("HATA:", e)

asyncio.run(main())
