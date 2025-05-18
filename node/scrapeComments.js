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

  const rawComments = await page.evaluate((max) => {
    const results = [];
  
    const items = document.querySelectorAll('div[data-e2e="comment-list-item"]');
    items.forEach(item => {
      const textNode = item.querySelector('p');
      const authorNode = item.querySelector('a[href*="/@"] > p');
      const timestampNode = item.querySelector('span[class*="SpanOtherInfos"]');
      const likesNode = item.querySelector('span[data-e2e="like-count"]');
  
      const text = textNode?.innerText?.trim();
      const author = authorNode?.innerText?.trim();
      const timestamp = timestampNode?.innerText?.trim();
      const likes = likesNode?.innerText?.trim();
  
      if (text && text.length > 2 && !results.some(c => c.text === text)) {
        results.push({
          text,
          author: author || null,
          timestamp: timestamp || null,
          likes: likes || null
        });
      }
    });
  
    return results.slice(0, max);
  }, max);
  
  const uniqueComments = Array.from(new Map(rawComments.map(obj => [obj.text, obj])).values()).slice(0, max);

  await browser.close();
  return {
    success: true,
    comment_count: uniqueComments.length,
    comments: uniqueComments
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
