import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta

#First load the credentials from the .env file
load_dotenv()

#Store the credentials in local variables
USER = os.getenv("BOX_USER")
PASSWORD = os.getenv("BOX_PASSWORD")
API_URL = os.getenv("BOX_API_URL")

LOGIN_URL="https://crosshero.com/athletes/sign_in"
CLASSES_URL= "https://crosshero.com/dashboard/classes"
RESERVATION_URL = "https://crosshero.com/dashboard/class_reservations"

def book_class():
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = session.get(API_URL, headers=headers)

    if response.status_code != 200:
        print(f"Error loading login page. Code: {response.status_code}")
        return None

    # Parse the HTML to search the hidden token
    soup = BeautifulSoup(response.text, 'html.parser')
    token_input = soup.find('input', {'name': 'authenticity_token'})

    if token_input:
        authenticity_token = token_input.get('value')
    else:
        print("Could not find autenticity token in the HTML.")
        return None

    # Data to do the login call
    login_payload = {
        "authenticity_token": authenticity_token,
        "password_mode": "1",
        "athlete[email]": USER,
        "athlete[password]": PASSWORD
    }

    login_response = session.post(LOGIN_URL, data=login_payload, headers=headers, allow_redirects=True)

    # Check if redirection no longer contains 'sign_in'
    if "sign_in" not in login_response.url:

        # Navigate to Classes using the active sesion
        response_classes = session.get(CLASSES_URL, headers=headers)
        soup_classes = BeautifulSoup(response_classes.text, 'html.parser')
        
        if response_classes.status_code == 200:

            found_class_id = obtain_class_id(session, headers)

            if not found_class_id:
                print("Could not find class Id.")
                return session

            # Refresh token in case a new one is needed for reservation
            token_reserva_input = soup_classes.find('input', {'name': 'authenticity_token'})
            token_reserva = token_reserva_input.get('value') if token_reserva_input else authenticity_token

            booking_payload = {
                "authenticity_token": token_reserva,
                "redirect_to": "",
                "fullscreen": "",
                "class_reservation[single_class_id]": found_class_id
            }

            res_reserva = session.post(RESERVATION_URL, data=booking_payload, headers=headers, allow_redirects=True)

            if res_reserva.status_code == 200 or res_reserva.status_code == 302:
                print("Booking successful!!")
            else:
                print(f"There was a problem with the reservation. Code: {res_reserva.status_code}")          
        else:
            print(f"Could not load classes page. Code: {response_classes.status_code}")
            
        return session
    else:
        print("Login failed. Check user and pwd in .env file.")
        return None

def obtain_class_id(session, headers):
    #Renavigate to classes URL for fresh sesion (maybe unnecessary)
    session.get(CLASSES_URL, headers=headers)

    # Get desired class date
    tomorrow = datetime.now() + timedelta(days=1)

    day_of_week = tomorrow.weekday()

    if day_of_week in [0, 1, 2, 4]:
        class_time = "17:00"
    elif day_of_week is 5:
        class_time = "10:00"
    else:
        return

    dias_es = {'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mié', 'Thu': 'Jue', 'Fri': 'Vie', 'Sat': 'Sáb', 'Sun': 'Dom'}
    dia_str = dias_es[tomorrow.strftime('%a')]
    fecha_str = tomorrow.strftime(f"{dia_str} %d/%m/%Y")

    program_id = "5cfad026801ff6003b64203c" # Id belonging to "OPEN WOD-" program, must be changed if another program is desired
    url_filtrada = f"{CLASSES_URL}?date={fecha_str}&program_id={program_id}"

    # Request to obtain HTML with classes belonging to selected date and program
    classes_response = session.get(url_filtrada, headers=headers)

    if classes_response.status_code != 200:
            print("Could not access class list.")
            return

    soup_classes = BeautifulSoup(classes_response.text, 'html.parser')
    class_id = None

    # This type was found as the correct one to search for by saving the response HTML and looking for times like "17:00"
    # It searches for the calculated class time defined in the previous hardcoded contidion, must be changed for different outcome
    for option in soup_classes.find_all('option'):
        if class_time in option.get_text():
            class_id = option.get('value')
            break

    if not class_id:
        print("No classes for tomorrow at 17:00 were found.")
        return

    print("¡Class Id obtained!")
    return class_id

if __name__ == "__main__":
    book_class()

