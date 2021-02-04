import requests
from bs4 import BeautifulSoup
from pytrovich.enums import NamePart, Gender, Case
from pytrovich.maker import PetrovichDeclinationMaker

def get_next_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        url = "https://vk.com/" + \
              soup.find("div", class_="catalog_wrap").find_all("div", class_="column4")[-1].find_all("a")[-1]["href"]
        return url
    else:
        return "Error"

def get_last_vk_id():
    """Получение id последнего пользователя, зарегестрироавшегося в Вконтакте."""
    url = "https://vk.com/catalog.php"
    while True:
        try:
            url = get_next_url(url)
        except IndexError:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                user_id = \
                soup.find("div", class_="catalog_wrap").find_all("div", class_="column2")[-1].find_all("a")[-1]["href"][
                2:]
                return int(user_id)
            else:
                return "Error"


maker = PetrovichDeclinationMaker()

def decline(username):
    """Возвращает имя и фамилию в родительном падаже."""
    first_name, last_name = username.split(" ")
    first_name = maker.make(NamePart.FIRSTNAME, Gender.MALE, Case.GENITIVE, first_name)
    last_name = maker.make(NamePart.LASTNAME, Gender.MALE, Case.GENITIVE, last_name)
    return first_name + " " + last_name