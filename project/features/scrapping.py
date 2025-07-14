import warnings
warnings.filterwarnings('ignore', category=UserWarning)
from playwright.sync_api import sync_playwright, Playwright, Page
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional
from .consultas import *


def get_page(p:Playwright, hl:bool=True) -> Page:
	"""Cria uma Navegador Chrome headless ou não e retorna uma página pronta para ser usada."""
	browser = p.chromium.launch(headless=hl)
	context = browser.new_context(
		locale='pt-BR',
		# user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
		viewport={'width': 1920, 'height': 1080}
	)
	page = context.new_page()
	return page


def get_prices(page:Page, org:str, dst:str, ida:datetime, volta:datetime) -> tuple[list[int], str]:
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
	page.wait_for_timeout(500)
	try:
		page.set_default_timeout(1500)
		span = page.locator('span', has_text='Mostrar mais voos').nth(0)
		span.click()
		page.wait_for_timeout(300)
	except Exception as e:
		pass
			

	html = page.content()
	soup = BeautifulSoup(html, 'html.parser')
	url = page.url
	page.context.close()

	precos_str = soup.select('ul > li > div > div > div > div > div > div > div > div > span[role="text"]')
	precos_int = [int(re.sub(r'\D', '', preco.get_text())) for preco in precos_str[:len(precos_str)//2]]
	precos_int.sort()

	return precos_int[:5], url


def pesquisar(org:str, dst:str, ida_inicio:str, ida_fim:str, periodo:int, target:int) -> Optional[pd.DataFrame]:
	# Verificar o código IATA
	if not consultar_aeroporto(org.upper()) or not consultar_aeroporto(dst.upper()):
		raise Exception('Aeroporto de origem ou destino não foi encontrado.')
	# Verificar as datas
	ida_inicio_f = consultar_data(ida_inicio)
	ida_fim_f = consultar_data(ida_fim)
	if not ida_inicio_f or not ida_fim_f:
		raise Exception('Alguma data inserida não é válida.')
	# Verificar o tipo das variáveis de periodo(dias) e preco(target)
	if not isinstance(periodo, int) or not isinstance(target, int):
		raise Exception('Período e preço precisam ser do tipo inteiros.')
	if periodo < 2: periodo = 2
	matches = []    
	intervalo = ida_fim_f - ida_inicio_f
	for i in range(intervalo.days+1):
		with sync_playwright() as p:
			for n in range(periodo-2, periodo+3):
				ida = ida_inicio_f + timedelta(days=i)
				volta = ida + timedelta(days=n)
				page = get_page(p, True)
				precos, url = get_prices(page, org.upper(), dst.upper(), ida, volta)
				if precos:
					for preco in precos:
						if preco <= target*1.05:
							matches.append({'origem': org.upper(), 'destino': dst.upper(), 'ida': ida, 'volta': volta, 'preco': preco, 'url': url})
	if matches:
		df = pd.DataFrame(matches)
		return df
	else:
		return None


if __name__ == '__main__':
	pass