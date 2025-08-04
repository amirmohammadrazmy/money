const puppeteer = require("puppeteer");
const fs = require("fs").promises;
const path = require("path");

const INPUT_FILE = "cutt_links.txt";

(async () => {
  let browser;
  try {
    console.log("🚀 Launching browser...");
    browser = await puppeteer.launch({
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--dns-server=8.8.8.8", // Still good practice for container environments
      ],
    });

    console.log(`📄 Reading links from ${INPUT_FILE}...`);
    const content = await fs.readFile(path.resolve(INPUT_FILE), "utf-8");
    const urlsToVisit = content.split("\n").map(line => line.trim()).filter(Boolean);

    console.log(`🔗 Found ${urlsToVisit.length} links to visit.`);

    for (let i = 0; i < urlsToVisit.length; i++) {
      const url = urlsToVisit[i];
      console.log(`[${i + 1}/${urlsToVisit.length}] Visiting: ${url}`);
      let newTab = null;
      try {
        newTab = await browser.newPage();
        await newTab.setRequestInterception(true);
        newTab.on('request', (req) => {
          if (['image', 'stylesheet', 'font'].includes(req.resourceType())) {
            req.abort();
          } else {
            req.continue();
          }
        });

        await newTab.goto(url, {
          waitUntil: "domcontentloaded",
          timeout: 20000, // 20 second timeout per link
        });

        console.log(`  ... waiting 3 seconds.`);
        await new Promise(r => setTimeout(r, 3000));

        console.log('  ✅ Success.');

      } catch (err) {
        console.error(`  ❌ Error visiting ${url}:`, err.message);
      } finally {
        if (newTab) {
          await newTab.close();
        }
      }
    }
  } catch (err) {
    console.error("❌ A critical error occurred:", err);
    process.exit(1);
  } finally {
    if (browser) {
      await browser.close();
    }
    console.log("🎉 All links visited. Script finished.");
    process.exit(0);
  }
})();
