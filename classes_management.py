from requests import Session
from bs4 import BeautifulSoup
from config import CLASSES_URL, RESERVATION_URL, PROGRAM_IDS, PUBLICATION_LEAD_TIME
from datetime import datetime, timedelta


def get_class_id(session: Session, headers: dict, program = "OPEN WOD-"):
    if program not in PROGRAM_IDS:
        raise ValueError(f"Unknown program '{program}'. Valid options are: {', '.join(PROGRAM_IDS.keys())}")

    #Renavigate to classes URL for fresh sesion (maybe unnecessary)
    session.get(CLASSES_URL, headers=headers)

    # Obtains the reservation date in the correct fotmat
    # Programs are published 25h in advance 
    target_class_date = datetime.now() + timedelta(hours=PUBLICATION_LEAD_TIME)
    dias_es = {'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mié', 'Thu': 'Jue', 'Fri': 'Vie', 'Sat': 'Sáb', 'Sun': 'Dom'}
    dia_str = dias_es[target_class_date.strftime('%a')]
    target_class_day = target_class_date.strftime(f"{dia_str} %d/%m/%Y")
    target_class_time = target_class_date.strftime("%H:00")

    # Adds the obtained date format and program to the URL
    filtered_url = f"{CLASSES_URL}?date={target_class_day}&program_id={PROGRAM_IDS[program]}"

    # Request to obtain HTML with classes belonging to selected date and program
    classes_response = session.get(filtered_url, headers=headers)

    if classes_response.status_code != 200:
            print("Could not access class list.")
            return []

    soup_classes = BeautifulSoup(classes_response.text, 'html.parser')

    # Finds the class ID for the target session based on the publication lead time    
    target_class_id = 0
    for option in soup_classes.find_all('option'):
        if target_class_time in option.get_text():
            target_class_id = option.get('value')

    if not target_class_id:
        print(f"No classes for tomorrow matching {target_class_time} were found.")
        return []

    print("¡Class Ids obtained!")
    return target_class_id



def book_class(class_id: list, valid_token: str, session: Session, headers: dict):

    booking_payload = {
        "authenticity_token": valid_token,
        "redirect_to": "",
        "fullscreen": "",
        "class_reservation[single_class_id]": class_id
    }

    res_reserva = session.post(RESERVATION_URL, data=booking_payload, headers=headers, allow_redirects=True)

    if res_reserva.status_code in [200, 302]:
        print("Booking successful!!")
    else:
        print(f"There was a problem with the reservation. Code: {res_reserva.status_code}")