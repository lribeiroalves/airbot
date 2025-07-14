from playwright.sync_api import sync_playwright, TimeoutError
import os
import shutil


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


def register_session():
	"""Abrir a sessao do whatsapp uma primeira vez para que seja lido o QR Code"""
	user_data_dir = ('project/whatsapp_sessao')

    # apagar sessao antiga
	if os.path.exists(user_data_dir):
		shutil.rmtree(user_data_dir)

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
		try:
			page.set_default_timeout(60000)
			page.fill('p:has(> br)', 'Eu')
			page.keyboard.press('Enter')
			page.wait_for_timeout(3000)
			print('Sessao registrada com sucesso.')
			page.context.close()
		except TimeoutError as e:
			print('Houve um erro ao tentar ler o QR Code, tente novamente.')


if __name__ == '__main__':
	register_session()