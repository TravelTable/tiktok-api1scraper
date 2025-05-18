import time
from typing import List, Dict
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_comments_headless(tiktok_url: str, max_comments: int = 50) -> Dict:
    options = uc.ChromeOptions()
    # options.add_argument("--headless")  # disable temporarily for debugging
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    driver = uc.Chrome(version_main=135, options=options, use_subprocess=True)
   
    print("🟢 Launching browser...")
    print(f"🔗 Navigating to: {tiktok_url}")

    driver.get(tiktok_url)

    comments = []
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"DivCommentListContainer")]'))
        )

        scroll_pause = 1
        last_height = driver.execute_script("return document.body.scrollHeight")

        while len(comments) < max_comments:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            # Expand replies if any
            expand_buttons = driver.find_elements(By.XPATH, '//p[contains(@class, "PReplyAction") and contains(text(), "View")]')
            for btn in expand_buttons:
                try:
                    driver.execute_script("arguments[0].click();", btn)
                except:
                    pass

            soup = BeautifulSoup(driver.page_source, "html.parser")
            comment_divs = soup.find_all("div", class_=lambda x: x and "DivCommentContentContainer" in x)

            for div in comment_divs:
                if len(comments) >= max_comments:
                    break
                text = div.get_text(separator=" ").strip()
                author = div.find_previous("span", class_=lambda x: x and "SpanUniqueId" in x)
                meta = div.find_previous("span", class_=lambda x: x and "SpanOtherInfos" in x)

                comments.append({
                    "text": text,
                    "author": author.text.strip() if author else None,
                    "timestamp": meta.text.strip() if meta else None,
                    "likes": None  # Optional: parse like count if visible
                })

    finally:
        driver.quit()

    return {
        "success": True,
        "comment_count": len(comments),
        "comments": comments
    }

if __name__ == "__main__":
    test_url = "https://www.tiktok.com/@catsmeowstory/video/7493560160296717573"
    result = fetch_comments_headless(test_url)
    print(result)
