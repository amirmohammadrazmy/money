import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            response = await page.goto("https://2ad.ir")
            print("Status:", response.status)
            content = await page.content()
            print("Page length:", len(content))
        except Exception as e:
            print("Error:", e)
        await browser.close()

asyncio.run(main())
