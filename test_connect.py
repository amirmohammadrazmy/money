import aiohttp
import asyncio
import sys

async def test():
    url = "https://2ad.ir/member/links"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as resp:
                status = resp.status
                print(f"Status code: {status}")
                if status == 200:
                    print("Connection successful!")
                    sys.exit(0)  # موفق
                else:
                    print(f"Failed to connect, status: {status}")
                    sys.exit(1)  # ناموفق
    except Exception as e:
        print(f"Exception occurred: {e}")
        sys.exit(1)  # ناموفق

asyncio.run(test())
