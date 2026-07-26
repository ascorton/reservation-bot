import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("BOX_USER")
PASSWORD = os.getenv("BOX_PASSWORD")
API_URL = os.getenv("BOX_API_URL")

LOGIN_URL="https://crosshero.com/athletes/sign_in"
CLASSES_URL= "https://crosshero.com/dashboard/classes"
RESERVATION_URL = "https://crosshero.com/dashboard/class_reservations"