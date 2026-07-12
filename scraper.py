import re

from playwright.sync_api import sync_playwright


def clean_price(price_text):
    digits_only = re.sub(r"[^\d]", "", price_text)

    if not digits_only:
        raise ValueError("Valid price could not be found.")

    return int(digits_only)


def scrape_product(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            title = page.title().strip()

            price_text = page.locator(
                ".product-price"
            ).first.inner_text(timeout=15000)

            price = clean_price(price_text)

            return {
                "title": title,
                "price": price,
                "price_text": price_text.strip(),
                "url": url,
                "site": "Star Tech"
            }

        finally:
            browser.close()


if __name__ == "__main__":
    test_url = input("Enter product URL: ")
    result = scrape_product(test_url)
    print(result)