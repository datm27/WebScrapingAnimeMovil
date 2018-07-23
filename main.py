import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib import request
import os

class Anime:
	def __init__(self, soup_main_page):
		self.soup_main_page = soup_main_page
		#self.soup_download_page = soup_download_page
		self.name = self.__getName__()
		self.synopsis = self.__getSynopsis__()
		self.genders = self.__getGenders__()
		self.num_caps = self.__getNumCaps__()
		self.url_download_mode = self.__getURLDownloadMode__()
		self.soup_download_page = self.__getSoupDownloadPage__()
		self.chapters = self.__generateChapters__()
	
	def __getName__(self):
		result = self.soup_main_page.find('h1').get_text()
		return result
	
	def __getSynopsis__(self):
		result = self.soup_main_page.find_all('div')[22].get_text()
		return result
	
	def __getGenders__(self):
		result = []
		genders_container = self.soup_main_page.find_all('div')[20].find_all('a')
		for i in range(genders_container.__len__()):
			result.append(genders_container[i].get_text())
		return result

	def __getNumCaps__(self):
		number_caps_container_str = self.soup_main_page.find(id="showEpisodes").find('span').get_text()
		result = getNumsOnString(number_caps_container_str)[0]
		return result

	def __getURLDownloadMode__(self):
		url_download_mode_container = self.soup_main_page.find_all('a')[4]
		url_download_mode = "https://animemovil.com{}".format(url_download_mode_container.attrs['href'])
		return url_download_mode

	def __getSoupDownloadPage__(self):
		response = requests.get(self.url_download_mode)
		soup_download_page = BeautifulSoup(response.content, "html.parser")
		return soup_download_page

	def __generateChapters__(self):
		ascontainer = self.soup_download_page.find(id="showEpisodes").find_all('a')
		chapters_reverse = []	# Capitulos en modo invertido

		for i in range(ascontainer.__len__()):
			title = ascontainer[i].attrs['title']
			episode = getNumsOnString(ascontainer[i].find('span').get_text())[0]
			caps_agruped = getNumsOnString(title)
			url_download = ascontainer[i].attrs['href']
			
			chapter = Chapter(episode, title, caps_agruped, url_download)
			chapters_reverse.append(chapter)

		chapters_reverse.reverse()	# Ordenando capitulos
		return chapters_reverse

	def downloadChapter(self, num):
		pass

class Chapter:
	def __init__(self, episode, title, caps_agruped, url_download):
		self.episode = episode
		self.title = title
		self.caps_agruped = caps_agruped
		self.url_download = url_download
		self.num_caps_agruped = len(caps_agruped)

	def download(self, Anime):
		ruta = "Downloads/" + Anime.name
		if self.num_caps_agruped == 1:
			request.urlretrieve("https:{}".format(self.url_download), "{}/{}.mp4".format(ruta, self.caps_agruped[0]))
		elif self.num_caps_agruped == 2:
			request.urlretrieve("https:{}".format(self.url_download), "{}/{} y {}.mp4".format(ruta, self.caps_agruped[0], self.caps_agruped[1]))

class Selector:
	def __init__(self, q):
		self.q = q
		self.anime_found_container = self.generateAnimeFoundContainer()
		self.anime_titles = self.generateAnimeTitles()
		self.anime_urls = self.generateAnimeURLs()
		self.size = self.generateSize()

	def generateAnimeFoundContainer(self):
		session = HTMLSession()
		data = {}
		data['q'] = self.q
		selector_response = session.get("https://animemovil.com/anime", params = data)
		selector_response.html.render()
		anime_found_container = selector_response.html.find(".hovers", first = True).find("li")

		return anime_found_container

	def generateAnimeTitles(self):
		anime_titles = []
		for item in self.anime_found_container:
			anime_title = item.find("span", first=True).text
			anime_titles.append(anime_title)

		return anime_titles

	def generateAnimeURLs(self):
		anime_urls = []
		for item in self.anime_found_container:
			anime_url = "https://animemovil.com" + item.find("a", first=True).attrs['href']
			anime_urls.append(anime_url)

		return anime_urls

	def generateSize(self):
		size = len(self.anime_found_container)
		return size
		
def SelectAnime():
	print()
	print("WEB SCRAPING (www.animemovil.com)")
	print("---------------------------------")
	anime_name = input("Ingrese nombre del anime: ")
	selector = Selector(anime_name)

	print()
	print("Lista de animes encontrados: ")

	print()
	for i in range(selector.size):
		print("	<{}> {}".format(i+1, selector.anime_titles[i]))
	
	print()
	option = int(input("Opcion: "))

	# Lo de abajo no va

	response_test = requests.get(selector.anime_urls[option-1])
	
	soup = BeautifulSoup(response_test.content, "html.parser")
	an = Anime(soup)

	return an

def checkDir(an):
	os.getcwd()
	dir = os.listdir('.')

	if "Downloads" not in dir:
		os.mkdir("Downloads")

	os.chdir("Downloads")

	dir = os.listdir('.')
	if an.name not in dir:
		os.mkdir(an.name)

	os.chdir('..')

def execute_option_1(an):
	print()
	print("DATOS DEL ANIME:")
	print()
	print("> Nombre: {}".format(an.name))
	print()
	print("> Generos: ", end="")
	print(", ".join(an.genders))
	print()
	print("> Número de capitulos: {}".format(an.num_caps))
	print()
	print("> Sinopsis: {}".format(an.synopsis))
	print()
	input("Presione ENTER para regresar al menu principal...")

def execute_option_2(an):
	print()
	print("LISTA DE CAPITULOS")
	print()

	for chapter in an.chapters:
		print(chapter.title)

	print()
	input("Presione ENTER para regresar al menu principal...")

def execute_option_3(an):
	print()
	print("SE EMPEZARAN A DESCARGAR TODOS LOS EPISODIOS")

	checkDir(an)
	for chapter in an.chapters:
		chapter.download(an)
		if chapter.num_caps_agruped == 1:
			print("Capitulo {} descargado.".format(chapter.caps_agruped[0]))
		elif chapter.num_caps_agruped == 2:
			print("Capitulos {} y {} descargados.".format(chapter.caps_agruped[0], chapter.caps_agruped[1]))

	print()
	print("Se descargaron todos los episodios.")
	print()
	input("Presione ENTER para regresar al menu principal...")

def execute_option_4(an):
	print()
	print("DESCARGA DE INTERVALO DE EPISODIOS")
	print()
	print("Ingrese los capitulos extremos: (Se incluyen los extremos)")
	num_chapter_0 = int(input("Ingrese el numero del anime inicial: "))
	num_chapter_f = int(input("Ingrese el numero del anime final: "))
	print()

	checkDir(an)

	for chapter in an.chapters:
		if chapter.num_caps_agruped == 1:
			if num_chapter_0 <= chapter.caps_agruped[0] and chapter.caps_agruped[0] <= num_chapter_f:
				chapter.download(an)
				print("Capitulo {} descargado.".format(chapter.caps_agruped[0]))
		if chapter.num_caps_agruped == 2:
			if (num_chapter_0 <= chapter.caps_agruped[0] and chapter.caps_agruped[0] <= num_chapter_f) or (num_chapter_0 <= chapter.caps_agruped[1] and chapter.caps_agruped[1] <= num_chapter_f):
				chapter.download(an)
				print("Capitulos {} y {} descargados.".format(chapter.caps_agruped[0], chapter.caps_agruped[1]))

	print()
	print("Se descargo el rango de episodios indicado.")
	print()
	print("Presione ENTER para regresar al menu principal...")

def execute_option_5(an):
	print()
	print("DESCARGA DE EPISODIOS")
	print()
	episodes_str_input = input("Ingrese espisodios separados por comas: ")
	episodes_str = episodes_str_input.replace(" ", "")
	episodes_list_str = episodes_str.split(",")

	episodes_list = []
	episodes_downloaded = []
	for num_str in episodes_list_str:
		episodes_list.append(int(num_str))

	checkDir(an)

	for chapter in an.chapters:
		for episode in episodes_list:
			if chapter.num_caps_agruped == 1 and episode not in episodes_downloaded:
				if chapter.caps_agruped[0] == episode:
					chapter.download(an)
					episodes_downloaded.append(chapter.caps_agruped[0])
					print("Capitulo {} descargado.".format(chapter.caps_agruped[0]))

			elif chapter.num_caps_agruped == 2 and episode not in episodes_downloaded:
				if chapter.caps_agruped[0] == episode or chapter.caps_agruped[1] == episode:
					chapter.download(an)
					episodes_downloaded.append(chapter.caps_agruped[0])
					episodes_downloaded.append(chapter.caps_agruped[1])
					print("Capitulos {} y {} descargados.".format(chapter.caps_agruped[0], chapter.caps_agruped[1]))

	print()
	print("Se descargaron los episodios ingresados.")
	print()
	input("Presione ENTER para regresar al menu principal...")

def getNumsOnString(text): # Mejorar el codigo
	numeros = []
	i = 0
	final = False
	while i < len(text) and  not final:
		while not text[i].isdigit():
			i = i + 1
			if i == len(text):
				final = True
				break
		num = []
		if i == len(text):
			final = True
			break
		while text[i].isdigit():
			num.append(text[i])
			i = i + 1
			if i == len(text):
				final = True
				break
		numeros.append(int("".join(num)))

	return numeros

def test(an):
	print(type(an.chapters))

def test2():
	SelectAnime()

def main_menu(an):
	print()
	print("WEB SCRAPING (www.animemovil.com)")
	print("---------------------------------")
	print("	<1> Informacion del anime")
	print("	<2> Mostrar capitulos")
	print("	<3> Descargar todos los capitulos")
	print("	<4> Descargar capitulos entre 2 valores")
	print("	<5> Seleccionar capitulos para descargar")
	print("	<6> Buscar otro anime")
	print("	<7> Salir")
	option = input("Opcion: ")

	if option == '1':
		execute_option_1(an)
	elif option == '2':
		execute_option_2(an)
	elif option == '3':
		execute_option_3(an)
	elif option == '4':
		execute_option_4(an)
	elif option == '5':
		execute_option_5(an)
	elif option == '6':
		return 1
	elif option == '7': # Opcion secreta para testear
		exit()
	else:
		option = print("No existe esa opcion, se cerrara el programa...")
		exit()

def run():
	an = SelectAnime()

	bucle_status = 2

	while True:
		if bucle_status == 1:
			an = SelectAnime()
			bucle_status = 2

		while bucle_status == 2:
			bucle_status = main_menu(an)
			if bucle_status == None:
				bucle_status = 2

if __name__ == '__main__':
	run()
	#test2()