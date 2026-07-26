
from requests import Session
from bs4 import BeautifulSoup
from config import CLASSES_URL, RESERVATION_URL
from datetime import datetime, timedelta

OPEN_WOD_ID = "5cfad026801ff6003b64203c"

def get_classes_ids(session: Session, headers: dict):
    #Renavigate to classes URL for fresh sesion (maybe unnecessary)
    session.get(CLASSES_URL, headers=headers)

    tomorrow = datetime.now() + timedelta(days=1)
    dias_es = {'Mon': 'Lun', 'Tue': 'Mar', 'Wed': 'Mié', 'Thu': 'Jue', 'Fri': 'Vie', 'Sat': 'Sáb', 'Sun': 'Dom'}
    dia_str = dias_es[tomorrow.strftime('%a')]
    fecha_str = tomorrow.strftime(f"{dia_str} %d/%m/%Y")

    filtered_url = f"{CLASSES_URL}?date={fecha_str}&program_id={OPEN_WOD_ID}"

    # Request to obtain HTML with classes belonging to selected date and program
    classes_response = session.get(filtered_url, headers=headers)

    if classes_response.status_code != 200:
            print("Could not access class list.")
            return []

    soup_classes = BeautifulSoup(classes_response.text, 'html.parser')

    class_times = get_class_times(tomorrow)

    if not class_times:
        print(f"No classes will be booked for tomorrow ({tomorrow.strftime('%A')}).")
        return []

    class_ids = []
    # This type was found as the correct one to search for by saving the response HTML and looking for times like "17:00"
    # It searches for the calculated class time defined in the previous hardcoded contidion, must be changed for different outcome
    for option in soup_classes.find_all('option'):
        for time in class_times:
            if time in option.get_text():
                class_id = option.get('value')
                if class_id and class_id not in class_ids:
                    class_ids.append(class_id)

    if not class_ids:
        print(f"No classes for tomorrow matching {class_times} were found.")
        return []

    print("¡Class Ids obtained!")
    return class_ids

def get_class_times(tomorrow: datetime):
    day_of_week = tomorrow.weekday()
    
    if day_of_week in [0, 1, 2, 4]:
        class_times = ["17:00", "18:00"]
    elif day_of_week == 5:
        class_times = ["10:00"]
    else:
        return []

    return class_times

def book_class(class_ids: list, valid_token: str, session: Session, headers: dict):
    
    for class_id in class_ids:
    
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