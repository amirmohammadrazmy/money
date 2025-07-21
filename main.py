import asyncio
from playwright.async_api import async_playwright

INPUT_FILES = ["download_links_480p.txt", "output_links.txt"]
OUTPUT_FILE = "final_shortened_links.txt"

USERNAME = "behtarinarts@gmail.com"
PASSWORD = "amir1384328"

LOGIN_URL = "https://2ad.ir/auth/signin"
LINKS_PAGE = "https://2ad.ir/member/links"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        page = await context.new_page()

        # لاگین
        await page.goto(LOGIN_URL)
        await page.fill('input[name="username"]', USERNAME)
        await page.fill('input[name="password"]', PASSWORD)
        await page.click('button#g-recaptcha, button#invisibleCaptchaSignin, button.submit-button')
        await page.wait_for_url(LINKS_PAGE)

        # رفتن به صفحه لینک‌ها
        await page.goto(LINKS_PAGE)

        # خواندن لینک‌ها از هر دو فایل و حذف تکراری‌ها
        all_links = set()
        for file_name in INPUT_FILES:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    for line in f:
                        url = line.strip()
                        if url:
                            all_links.add(url)
            except FileNotFoundError:
                print(f"File {file_name} not found, skipping.")

        print(f"Total unique links to shorten: {len(all_links)}")

        # ذخیره لینک‌های کوتاه شده (برای جلوگیری از تکرار)
        shortened_links = set()
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f_out:
                for line in f_out:
                    shortened_links.add(line.strip())
        except FileNotFoundError:
            pass

        with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
            for url in all_links:
                if url in shortened_links:
                    print(f"Already shortened: {url}")
                    continue

                # کلیک روی دکمه لینک جدید
                await page.click('#modal-open-new-link')

                # پر کردن فرم لینک
                await page.fill('input#url', url)

                # کلیک روی دکمه کوتاه کن
                await page.click('span:has-text("کوتاه کن")')

                # صبر برای نمایش لینک کوتاه شده
                await page.wait_for_selector('input#link-result-url')

                # گرفتن لینک کوتاه شده
                short_link = await page.eval_on_selector('input#link-result-url', 'el => el.value')

                # باز کردن لینک کوتاه شده در تب جدید (برای ثبت درآمد)
                new_page = await context.new_page()
                await new_page.goto(short_link)
                await asyncio.sleep(3)  # صبر برای لود صفحه

                f_out.write(short_link + "\n")
                f_out.flush()
                shortened_links.add(url)

                print(f"Shortened: {url} -> {short_link}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
