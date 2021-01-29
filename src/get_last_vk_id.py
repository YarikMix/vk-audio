import requests
from bs4 import BeautifulSoup

HEADERS = {
	"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
}


def get_html(url, params=''):
	return requests.get(url, headers=HEADERS, params=params)


def get_next_url(html):
	if html.status_code == 200:
		soup = BeautifulSoup(html.content, 'html.parser')
		url = "https://vk.com/" + soup.find("div", class_="catalog_wrap").find_all("div", class_="column4")[-1].find_all("a")[-1]["href"] 
		return url
	else:
		return "Error"


def get_last_vk_id():
	url = "https://vk.com/catalog.php"
	while True:
		try:
			html = get_html(url)
			url = get_next_url(html)
		except IndexError:
			html = get_html(url)
			user_id = "Error"
			if html.status_code == 200:
				soup = BeautifulSoup(html.content, 'html.parser')
				user_id = soup.find("div", class_="catalog_wrap").find_all("div", class_="column2")[-1].find_all("a")[-1]["href"][2:]
			return int(user_id)