const puppeteer = require("puppeteer");
const fs = require("fs").promises;
const path = require("path");
const https = require("https");

const INPUT_FILES = ["download_links_480p.txt", "output_links.txt"];
const OUTPUT_FILE = "final_shortened_links.txt";

const USERNAME = "behtarinarts@gmail.com";
const PASSWORD = "amir1384328";

const LOGIN_URL = "https://2ad.ir/auth/signin";
const LINKS_PAGE = "https://2ad.ir/member/links";

function checkSiteAvailable(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, (res) => {
        const { statusCode } = res;
        if (statusCode >= 200 && statusCode < 400) {
          resolve(true);
        } else {
          reject(new Error(`Server responded with status code: ${statusCode}`));
        }
      })
      .on("error", (err) => {
        reject(new Error(`Site unreachable: ${err.message}`));
      });
  });
}

(async () => {
  try {
    console.log("🔍 در حال بررسی اتصال به سایت...");
    await checkSiteAvailable(LOGIN_URL);
    console.log("✅ سایت در دسترس است. ادامه می‌دهیم...");

    const browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    });

    const page = await browser.newPage();

    // لاگین
    await page.goto(LOGIN_URL, { waitUntil: "networkidle2" });
    await page.type('input[name="username"]', USERNAME);
    await page.type('input[name="password"]', PASSWORD);

    await Promise.all([
      page.click('button#g-recaptcha, button#invisibleCaptchaSignin, button.submit-button'),
      page.waitForNavigation({ waitUntil: "networkidle2" }),
    ]);

    await page.goto(LINKS_PAGE, { waitUntil: "networkidle2" });

    const allLinks = new Set();
    for (const file of INPUT_FILES) {
      try {
        const content = await fs.readFile(path.resolve(file), "utf-8");
        content
          .split("\n")
          .map((line) => line.trim())
          .filter(Boolean)
          .forEach((url) => allLinks.add(url));
      } catch (err) {
        console.log(`⚠️ فایل پیدا نشد: ${file} → رد شد.`);
      }
    }

    console.log(`🔗 تعداد لینک یکتا: ${allLinks.size}`);

    const shortenedLinks = new Set();
    try {
      const existing = await fs.readFile(path.resolve(OUTPUT_FILE), "utf-8");
      existing
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .forEach((url) => shortenedLinks.add(url));
    } catch (err) {
      // فایل نیست، مشکلی نیست
    }

    for (const url of allLinks) {
      if (shortenedLinks.has(url)) {
        console.log(`✅ قبلاً کوتاه شده: ${url}`);
        continue;
      }

      try {
        await page.click("#modal-open-new-link");
        await page.waitForSelector("input#url", { visible: true });
        await page.evaluate(() => {
          const input = document.querySelector("input#url");
          if (input) input.value = "";
        });
        await page.type("input#url", url);

        console.log('Current page URL:', page.url()); // For debugging

        const shortenButtonHandle = await page.evaluateHandle(() => {
          const spans = Array.from(document.querySelectorAll('span'));
          const button = spans.find(span => span.textContent.includes('کوتاه کن'));
          return button;
        });

        const shortenButton = shortenButtonHandle.asElement();

        if (!shortenButton) {
          console.error("❌ دکمه «کوتاه کن» با روش جدید پیدا نشد.");
          continue;
        }

        await Promise.all([
          shortenButton.click(),
          page.waitForSelector("input#link-result-url", { visible: true }),
        ]);

        const shortLink = await page.$eval("input#link-result-url", (el) => el.value);

        const newTab = await browser.newPage();
        await newTab.goto(shortLink, { waitUntil: "domcontentloaded" });
        await newTab.waitForTimeout(3000);
        await newTab.close();

        await fs.appendFile(path.resolve(OUTPUT_FILE), shortLink + "\n");
        shortenedLinks.add(url);

        console.log(`✅ کوتاه شد: ${url} → ${shortLink}`);
      } catch (err) {
        console.error(`❌ خطا در کوتاه‌سازی ${url}:`, err.message);
      }
    }

    await browser.close();
    console.log("🎉 تمام شد.");
  } catch (err) {
    console.error("❌ خطا:", err);
    process.exit(1);
  }
})();
