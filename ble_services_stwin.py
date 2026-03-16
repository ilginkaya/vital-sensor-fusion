import asyncio
from bleak import BleakClient

ADDRESS = "32CD2B95-DE67-D928-2653-98CFAB39DB49"

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Bağlandı:", client.is_connected)

        for service in client.services:
            print("\nSERVICE:", service.uuid)

            for char in service.characteristics:
                print("  CHAR:", char.uuid, "|", char.properties)

asyncio.run(main())
