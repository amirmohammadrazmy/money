const https = require("https");
const fs = require("fs").promises;
const path = require("path");

const INPUT_FILES = ["download_links_480p.txt", "output_links.txt"];
const OUTPUT_FILE = "final_shortened_links.txt";
const API_KEY = "d059ef376379b727b42de971184cdec641500561";

function shortenUrl(urlToShorten) {
  return new Promise((resolve, reject) => {
    const encodedUrl = encodeURIComponent(urlToShorten);
    const apiUrl = `https://2ad.ir/api?api=${API_KEY}&url=${encodedUrl}&format=text`;

    https.get(apiUrl, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode === 200 && data.startsWith('https://')) {
          resolve(data);
        } else {
          reject(new Error(`API returned an error: "${data}"`));
        }
      });
    }).on('error', (err) => reject(new Error(`HTTP request failed: ${err.message}`)));
  });
}

(async () => {
  try {
    console.log("🔗 Reading URLs from input files...");
    const allLinks = new Set();
    for (const file of INPUT_FILES) {
      try {
        const content = await fs.readFile(path.resolve(file), "utf-8");
        content.split("\n").map(line => line.trim()).filter(Boolean).forEach(url => allLinks.add(url));
      } catch (err) {
        console.log(`⚠️ Could not read file: ${file} → skipping.`);
      }
    }

    if (allLinks.size === 0) {
        console.log("No links found to process. Exiting.");
        return;
    }

    console.log(`Total unique links to process: ${allLinks.size}`);

    // Clear the output file before starting
    await fs.writeFile(path.resolve(OUTPUT_FILE), '');
    console.log(`Cleared ${OUTPUT_FILE} for new run.`);

    let successCount = 0;
    let errorCount = 0;

    for (const url of allLinks) {
      try {
        const shortUrl = await shortenUrl(url);
        await fs.appendFile(path.resolve(OUTPUT_FILE), shortUrl + "\n");
        console.log(`✅ ${url} → ${shortUrl}`);
        successCount++;
      } catch (err) {
        console.error(`❌ ${url} → ${err.message}`);
        errorCount++;
      }
      // Add a small delay to be polite to the API
      await new Promise(r => setTimeout(r, 50));
    }

    console.log(`\n🎉 Finished!`);
    console.log(`  - Success: ${successCount}`);
    console.log(`  - Failed:  ${errorCount}`);

  } catch (err) {
    console.error("❌ A critical script error occurred:", err);
    process.exit(1);
  }
})();
