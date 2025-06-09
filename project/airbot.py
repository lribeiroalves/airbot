from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto('https://www.decolar.com/shop/flights/results/roundtrip/GRU/CDG/2025-07-03/2025-07-11/1/0/0?from=SB&di=1', timeout=60000)
        page.wait_for_timeout(15000)
        page.goto('https://www.decolar.com/shop/flights/results/roundtrip/GRU/AMS/2025-07-03/2025-07-11/1/0/0?from=SB&di=1', timeout=60000)
        page.wait_for_timeout(5000)

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        preco = soup.select_one('span.price > p')
        
        print(preco)

        browser.close()


if __name__ == '__main__':
    main()