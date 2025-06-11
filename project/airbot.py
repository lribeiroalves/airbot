import warnings
warnings.filterwarnings('ignore', category=UserWarning)
from pyairports.airports import Airports
from playwright.sync_api import sync_playwright, Playwright, Page
from bs4 import BeautifulSoup, Tag
import re
from datetime import datetime
import pandas as pd


def get_page(p:Playwright, hl:bool=True) -> Page:
    """Cria uma Navegador Chrome headless ou não e retorna uma página pronta para ser usada."""
    browser = p.chromium.launch(headless=hl)
    context = browser.new_context(
        locale='pt-BR',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    page = context.new_page()
    return page


def get_prices(page:Page, org:str, dst:str, ida:datetime, volta:datetime) -> list[int]:
    """Acessa o site Google Flights, pesquisa uma viagem de ida e volta e retorna os 5 melhores preços para essa data em uma lista de inteiros"""
    page.goto('https://www.google.com/travel/flights', timeout=5000)
    page.wait_for_timeout(300)
    page.fill('input[aria-label="De onde?"]', org)
    page.wait_for_timeout(300)
    page.keyboard.press('Enter')
    page.fill('input[aria-label="Para onde? "]', dst)
    page.wait_for_timeout(300)
    page.keyboard.press('Enter')
    page.wait_for_timeout(300)
    page.fill('input[placeholder="Partida"]', ida.strftime('%d/%m/%Y'))
    page.wait_for_timeout(300)
    page.keyboard.press('Tab')
    page.fill('input[placeholder="Volta"]', volta.strftime('%d/%m/%Y'))
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
    page.context.close()

    precos_str = soup.select('ul > li > div > div > div > div > div > div > div > div > span[role="text"]')
    precos_int = [int(re.sub(r'\D', '', preco.get_text())) for preco in precos_str[:len(precos_str)//2]]
    precos_int.sort()

    return precos_int


def consultar_aeroporto(iata:str) -> bool:
    try:
        aeroportos = Airports()
        aeroporto = aeroportos.airport_iata(iata)
        return True if aeroporto else False
    except Exception as err:
        print(f"Erro ao consultar o aeroporto: {err}")
        return False
    

def consultar_data(data:str, formato:str='%d/%m/%Y') -> bool:
    try:
        datetime.strptime(data, formato)
        return True
    except ValueError as err:
        print(f'Data {data} inválida.')
        return False


def pesquisar(org:str, dst:str, ida_inicio:str, ida_fim:str, periodo:int, preco:int) -> pd.DataFrame:
    # Verificar o código IATA
    if not consultar_aeroporto(org) or not consultar_aeroporto(dst):
        raise Exception('Aeroporto de origem ou destino não foi encontrado.')
    # Verificar as datas
    if not consultar_data(ida_inicio) or not consultar_data(ida_fim):
        raise Exception('Alguma data innserida não é válida.')
    # Verificar o tipo das variáveis de periodo(dias) e preco(target)
    if not isinstance(periodo, int) or not isinstance(preco, int):
        raise Exception('Período e preço precisam ser inteiros.')


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
        page.fill('input[aria-label="Para onde? "]', 'MIA')
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
        # browser.close()
        page.context.close()

        precos_str = soup.select('ul > li > div > div > div > div > div > div > div > div > span[role="text"]')
        precos_int = [int(re.sub(r'\D', '', preco.get_text())) for preco in precos_str[:len(precos_str)//2]]
        precos_int.sort()

        for preco in precos_int[:5]:
            print(preco)


if __name__ == '__main__':
    pesquisas = [
        {'origem': 'PNZ', 'destino':'GRU', 'ida_inicio':'16/12/2025', 'ida_fim':'20/12/2025', 'periodo':30, 'preco': 700},
        {'origem': 'GRU', 'destino':'ZRH', 'ida_inicio':'28/11/2025', 'ida_fim':'30/11/2025', 'periodo':12, 'preco': 4000},
    ]

    for viagem in pesquisas:
        df = pesquisar(viagem['origem'], viagem['destino'], viagem['ida_inicio'], viagem['ida_fim'], viagem['periodo'], viagem['preco'])
        # continuar

    tempo = datetime.now()
    main()
    print(datetime.now() - tempo)