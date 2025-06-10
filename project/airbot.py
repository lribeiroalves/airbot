from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup, Tag
import re

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale='pt-BR',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        page.goto('https://www.google.com/travel/flights', timeout=5000)
        page.wait_for_timeout(300)

        page.fill('input[aria-label="De onde?"]', 'GRU')
        page.wait_for_timeout(300)
        page.keyboard.press('Enter')
        page.fill('input[aria-label="Para onde? "]', 'CDG')
        page.wait_for_timeout(300)
        page.keyboard.press('Enter')
        page.wait_for_timeout(300)
        page.fill('input[placeholder="Partida"]', '28/11/2025')
        page.wait_for_timeout(300)
        page.keyboard.press('Tab')
        page.fill('input[placeholder="Volta"]', '12/12/2025')
        page.wait_for_timeout(300)
        page.keyboard.press('Tab')
        page.wait_for_timeout(500)
        page.keyboard.press('Enter')
        page.wait_for_timeout(1000)
        page.screenshot(path='s.png')
        span = page.locator('span', has_text='Mostrar mais voos').nth(0)
        span.click()
        page.wait_for_timeout(300)

        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        browser.close()

        precos_str = soup.select('ul > li > div > div > div > div > div > div > div > div > span')
        precos_int = [int(re.sub(r'\D', '', preco.get_text())) for preco in precos_str[:len(precos_str)//2]]
        precos_int.sort()

        for preco in precos_int[:5]:
            print(preco)



if __name__ == '__main__':
    from datetime import datetime

    tempo = datetime.now()
    main()
    print(datetime.now() - tempo)