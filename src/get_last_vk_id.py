import requests
from bs4 import BeautifulSoup

HEADERS = {
	"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
}


def get_next_url(url):
	response = requests.get(url)
	if response.status_code == 200:
		soup = BeautifulSoup(response.content, 'html.parser')
		url = "https://vk.com/" + soup.find("div", class_="catalog_wrap").find_all("div", class_="column4")[-1].find_all("a")[-1]["href"] 
		return url
	else:
		return "Error"


def get_last_vk_id():
	url = "https://vk.com/catalog.php"
	while True:
		try:
			url = get_next_url(url)
		except IndexError:
			response = requests.get(url)
			if response.status_code == 200:
				soup = BeautifulSoup(response.content, 'html.parser')
				user_id = soup.find("div", class_="catalog_wrap").find_all("div", class_="column2")[-1].find_all("a")[-1]["href"][2:]
				return int(user_id)
			else:
				return "Error"