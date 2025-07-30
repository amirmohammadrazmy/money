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

// چک کردن در دسترس بودن سایت
function checkSiteAvailable(url) {
  return new Promise((resolve, reject) => {
    https.get(url, res => {
      const { statusCode } = res;
      if (statusCode >= 200 && statusCode < 400) {
        resolve(true);
      } else {
        reject(new Error(`Server responded with status code: ${statusCode}`));
      }
    }).on("error", err => {
      reject(new Error(`Site unreachable: ${err.message}`));
    });
  });
}

(async () => {
  try {
    console.log("🔍 در حال بررسی اتصال به سایت...");
    await checkSiteAvailable(LOGIN_URL);
    console.log("✅ سایت در دسترس است. ادامه می‌دهیم...");
  } catch (err) {
    console.error("❌ خطا: سایت در دسترس نیست.");
    console.error(err.message);
    process.exit(1);
  }

  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();

  // لاگین
  await page.goto(LOGIN_URL, { waitUntil: "networkidle2" });
  await page.type('input[name="username"]', USERNAME);
  await page.type('input[name="password"]', PASSWORD);
  await Promise.all([
    page.click('button#g-recaptcha, button#invisibleCaptchaSignin, button.submit-button'),
    page.waitForNavigation({ waitUntil: "networkidle2" })
  ]);

  // رفتن به صفحه لینک‌ها
  await page.goto(LINKS_PAGE, { waitUntil: "networkidle2" });

  // خوندن لینک‌ها
  const allLinks = new Set();
  for (const file of INPUT_FILES) {
    try {
      const content = await fs.readFile(path.resolve(file), "utf-8");
      content.split("\n").map(line => line.trim()).filter(Boolean).forEach(url => allLinks.add(url));
    } catch (err) {
      console.log(`File not found: ${file}, skipping.`);
    }
  }

  console.log(`Total unique links to shorten: ${allLinks.size}`);

  // لینک‌هایی که قبلاً ذخیره شدند
  const shortenedLinks = new Set();
  try {
    const existing = await fs.readFile(path.resolve(OUTPUT_FILE), "utf-8");
    existing.split("\n").map(line => line.trim()).filter(Boolean).forEach(url => shortenedLinks.add(url));
  } catch (err) {}

  const fOut = await fs.open(path.resolve(OUTPUT_FILE), "a");

  for (const url of allLinks) {
    if (shortenedLinks.has(url)) {
      console.log(`Already shortened: ${url}`);
      continue;
    }

    await page.click("#modal-open-new-link");
    await page.waitForSelector("input#url", { visible: true });
    await page.type("input#url", url);
    await page.click('span:contains("کوتاه کن")');
    await page.waitForSelector("input#link-result-url");

    const shortLink = await page.$eval("input#link-result-url", el => el.value);

    const newTab = await browser.newPage();
    await newTab.goto(shortLink, { waitUntil: "domcontentloaded" });
    await newTab.waitForTimeout(3000);
    await newTab.close();

    await fOut.appendFile(shortLink + "\n");
    shortenedLinks.add(url);

    console.log(`Shortened: ${url} -> ${shortLink}`);
  }

  await fOut.close();
  await browser.close();
})();
