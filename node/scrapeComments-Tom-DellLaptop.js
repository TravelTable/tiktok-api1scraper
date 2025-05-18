const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

async function scrapeComments(tiktokUrl, max = 50) {
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--start-maximized']
  });

  const page = await browser.newPage();
  console.log('🌐 Opening:', tiktokUrl);
  await page.goto(tiktokUrl, { waitUntil: 'networkidle2', timeout: 60000 });

  console.log("⏳ Scrolling to trigger comment load...");
  let scrollTries = 0;
  while (scrollTries < 25) {
    await page.evaluate(() => window.scrollBy(0, 1000));
    await sleep(1000);

    const foundText = await page.evaluate(() => {
      return Array.from(document.querySelectorAll("p"))
        .some(el => el.innerText && el.innerText.length > 10);
    });

    if (foundText) {
      console.log("✅ Comment-like paragraphs found!");
      break;
    }

    scrollTries++;
  }

  if (scrollTries === 25) {
    await page.screenshot({ path: "debug-comments.png", fullPage: true });
    throw new Error("❌ Comments never loaded. Screenshot saved as debug-comments.png");
  }

  let tries = 0;
  while (tries < 10) {
    await page.evaluate(() => window.scrollBy(0, 1000));
    await sleep(1000);
    tries++;
  }

    const comments = await page.evaluate((max) => {
    const paragraphs = Array.from(document.querySelectorAll("p"));
    const results = [];

    for (let p of paragraphs) {
      const text = p?.innerText?.trim();

      if (
        text &&
        text.length > 5 &&
        text.length < 300 &&
        !text.includes("like") &&
        !text.includes("Reply") &&
        !text.match(/^\d+$/)
      ) {
        // Try to extract parent context for author and likes
        const parent = p.closest('div[data-e2e="comment-list-item"]');

        const authorNode = parent?.querySelector('a[data-e2e="comment-user-name"]');
        const likesNode = parent?.querySelector('span[data-e2e="like-count"]');

        results.push({
          text,
          author: authorNode?.innerText?.trim() || null,
          timestamp: null, // Optional: fill later
          likes: likesNode?.innerText?.trim() || null
        });

        if (results.length >= max) break;
      }
    }

    return results;
  }, max);

  if (!rawComments || rawComments.length === 0) {
    await page.screenshot({ path: 'debug-comments.png', fullPage: true });
    console.warn('⚠️ No comments found. Screenshot saved as debug-comments.png');
  }

  await browser.close();

  return {
    success: true,
    comment_count: rawComments.length,
    comments: rawComments
  };
}

const url = process.argv[2];
const max = parseInt(process.argv[3]) || 50;

if (!url) {
  console.error('❌ Usage: node scrapeComments.js <TikTok URL> <max>');
  process.exit(1);
}

scrapeComments(url, max).then((data) => {
  console.log(JSON.stringify(data, null, 2));
}).catch((err) => {
  console.error('❌ Scraping failed:', err);
  process.exit(1);
});
