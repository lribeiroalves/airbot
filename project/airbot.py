from features.scrapping import pesquisar
from features.whatsapp import send_whatsapp
from datetime import datetime, timedelta


def airbot(pesquisas: list = []) -> None:
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


if __name__ == '__main__':
	pesquisas = [
		{'origem': 'PNZ', 'destino':'GRU', 'ida_inicio':'16/12/2025', 'ida_fim':'22/12/2025', 'periodo':30, 'preco': 950, 'enable': True},
		{'origem': 'GRU', 'destino':'MCO', 'ida_inicio':'01/05/2026', 'ida_fim':'15/05/2026', 'periodo':12, 'preco': 1500, 'enable': True},
		# {'origem': 'GRU', 'destino':'MUC', 'ida_inicio':'28/11/2025', 'ida_fim':'30/11/2025', 'periodo':11, 'preco': 3800, 'enable': True},
	]
	
	airbot(pesquisas=pesquisas)
