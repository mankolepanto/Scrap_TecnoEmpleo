from bs4 import BeautifulSoup
import requests

def get_soup(url):
    """Hace una solicitud GET a la URL y devuelve el objeto BeautifulSoup."""
    response = requests.get(url)

    return BeautifulSoup(response.content, 'html.parser')


def find_next_page(soup):
    """Busca y devuelve el enlace de la siguiente página, si existe."""
    next_page_tag = soup.find('a', class_='page-link', string='siguiente')
    return next_page_tag['href'] if next_page_tag else None