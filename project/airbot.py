import warnings
warnings.filterwarnings('ignore', category=UserWarning)
from pyairports.airports import Airports
from playwright.sync_api import sync_playwright, Playwright, Page
from bs4 import BeautifulSoup, Tag
import re
from datetime import datetime, timedelta
import pandas as pd
import os
from typing import Optional


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


def send_whatsapp(msg:str = ''):
	if msg == '':
		print('Mensagem vazia, cancelando envio para o Whatsapp')
		return
	
	user_data_dir = os.path.abspath("whatsapp_sessao")

	if not os.path.exists(user_data_dir):
		print('Sessao nao encontrada, sera necessario escanear o QR Code.')

	with sync_playwright() as p:
		browser = p.chromium.launch_persistent_context(
				user_data_dir,
				locale='pt-BR',
				headless=False,
				viewport={'width': 1800, 'height': 900}
		)
		page = browser.new_page()
		page.goto('https://web.whatsapp.com/')
		page.wait_for_timeout(5000)
		page.set_default_timeout(10000)
		page.fill('p:has(> br)', 'Passagens')
		page.keyboard.press('Enter')
		page.wait_for_timeout(300)
		page.fill('p:has(> br)', msg)
		page.keyboard.press('Enter')
		page.wait_for_timeout(500)
		page.context.close()


def consultar_aeroporto(iata:str) -> bool:
	try:
		aeroportos = Airports()
		aeroporto = aeroportos.airport_iata(iata)
		return True if aeroporto else False
	except Exception as err:
		print(f'Erro ao consultar o aeroporto: "{err}"')
		return False
		

def consultar_data(data:str, formato:str='%d/%m/%Y') -> Optional[datetime]:
	try:
		data_formatada = datetime.strptime(data, formato)
		return data_formatada
	except ValueError as err:
		print(f'Data {data} inválida.')
		return None


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
	pesquisas = [
		{'origem': 'PNZ', 'destino':'GRU', 'ida_inicio':'16/12/2025', 'ida_fim':'22/12/2025', 'periodo':30, 'preco': 950, 'enable': True},
		{'origem': 'GRU', 'destino':'MCO', 'ida_inicio':'01/05/2026', 'ida_fim':'15/05/2026', 'periodo':12, 'preco': 1500, 'enable': True},
		# {'origem': 'GRU', 'destino':'MUC', 'ida_inicio':'28/11/2025', 'ida_fim':'30/11/2025', 'periodo':11, 'preco': 3800, 'enable': True},
	]

	tempo_inical = datetime.now() - timedelta(minutes=31)
	intervalo_tempo = timedelta(minutes=30)

	while True:
		tempo = datetime.now()
		if tempo >= tempo_inical + intervalo_tempo:
			tempo_inical = tempo
			print('=' * 50)
			print(tempo.strftime('%d/%m/%Y - %H:%M:%S'))
			for viagem in pesquisas:
				if viagem['enable']:
					try:
						print(f'Buscando passagens para {viagem["origem"]}/{viagem["destino"]}')
						df = pesquisar(viagem['origem'], viagem['destino'], viagem['ida_inicio'], viagem['ida_fim'], viagem['periodo'], viagem['preco'])
						if df is not None:
							df.to_csv(f'Resultados_{viagem['origem']}_{viagem['destino']}.csv')
							send_whatsapp(df.to_string(index=False))
							print(f'Resultados enviados para o WhatsApp')
							viagem['enable'] = False
						else:
							print('Não foram encontrados resultados para o preço target.')
					except Exception as e:
						print(e)
				else:
					print(f'Preços para {viagem['origem']}/{viagem['destino']} já foram encontrados.')
			print(f'Próxima execução às {(tempo_inical+intervalo_tempo).strftime('%d/%m/%Y - %H:%M:%S')}')
			print('=' * 50, end='\n\n')
