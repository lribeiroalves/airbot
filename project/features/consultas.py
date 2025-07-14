from pyairports.airports import Airports
from datetime import datetime
from typing import Optional


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
	

if __name__ == '__main__':
	pass