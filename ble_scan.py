import asyncio
from bleak import BleakScanner

async def main():
    print("BLE cihazları taranıyor...\n")
    devices = await BleakScanner.discover(timeout=10)

    for d in devices:
        print("ADDRESS:", d.address)
        print("NAME:", d.name)
        print("--------------------")

asyncio.run(main())
