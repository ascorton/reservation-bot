import requests
from requests import Session
from bs4 import BeautifulSoup
from config import API_URL, CLASSES_URL, LOGIN_URL, USER, PASSWORD
from classes_management import get_classes_ids, book_class

def run_booking_script():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = session.get(API_URL, headers=headers)

    if response.status_code != 200:
        print(f"Error loading login page. Code: {response.status_code}")
        return None

    authenticity_token = get_authenticity_token(BeautifulSoup(response.text, 'html.parser'))

    if not authenticity_token:
        return None

    login_response = perform_login(session, headers, authenticity_token)

    if "sign_in" in login_response.url:
        print("Login failed. Check user and pwd in .env file.")
        return None

    response_classes = session.get(CLASSES_URL, headers=headers)
    soup_classes = BeautifulSoup(response_classes.text, 'html.parser')

    if response_classes.status_code != 200:
        print(f"Could not load classes page. Code: {response_classes.status_code}")

    found_classes_ids = get_classes_ids(session, headers)

    if not found_classes_ids:
        print("Could not find any class id for the specified parameters.")
        return session

    token_reserva_input = soup_classes.find('input', {'name': 'authenticity_token'})
    token_reserva = token_reserva_input.get('value') if token_reserva_input else authenticity_token

    book_class(found_classes_ids, token_reserva, session, headers)

    return session

def get_authenticity_token(soup: BeautifulSoup):
    token_input = soup.find('input', {'name': 'authenticity_token'})

    if not token_input:
        print("Could not find autenticity token in the HTML.")
        return None

    return token_input.get('value')


def perform_login(session: Session, headers: dict[str,str], token: str):
    login_payload = {
        "authenticity_token": token,
        "password_mode": "1",
        "athlete[email]": USER,
        "athlete[password]": PASSWORD
    }

    return session.post(LOGIN_URL, data=login_payload, headers=headers, allow_redirects=True)