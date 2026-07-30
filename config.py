import os
from pathlib import Path
from dotenv import load_dotenv
 
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

USER = os.getenv("BOX_USER")
PASSWORD = os.getenv("BOX_PASSWORD")
API_URL = os.getenv("BOX_API_URL")

LOGIN_URL="https://crosshero.com/athletes/sign_in"
CLASSES_URL= "https://crosshero.com/dashboard/classes"
RESERVATION_URL = "https://crosshero.com/dashboard/class_reservations"

# IDs obtained from the Crossfit website
PROGRAM_IDS = {
    "CROSSFIT-": "5aae9c5a58c1f300327f28a4",
    "CLUB TEAM TRAINING": "5db19a439815df00414a5a5b",
    "CROSSFIT": "67c02541b1c7a7ebecbf1d1b",
    "CROSSFIT B": "68b5c8f4e1a84161a425f128",
    "GYMNASTICS": "5aae9c7458c1f300327f28b4",
    "HYBRID CROSSFIT": "5c1d285f6c061b003a0c3382",
    "HYROX": "67c02b5b8f3342385c953acf",
    "OPEN 26.3": "6044096cac9717004251c328",
    "OPEN BOX": "5aae9cf41e14bf00322b2cff",
    "OPEN WOD": "67c02bbd296f5f59e7e676f0",
    "OPEN WOD-": "5cfad026801ff6003b64203c",
    "WEIGHTLIFTING": "5aae9d181e14bf00322b2d01",
    "YOGA": "5aae9d3c58c1f300327f28ed",
}

# hours in advance to book the class 
PUBLICATION_LEAD_TIME = 25