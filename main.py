from booking import run_booking_script
import time
import schedule

def run_job():
    print("Executing class booking")
    run_booking_script()

schedule.every().day.at("16:00").do(run_job)

print("Booking bot initiated. Awaiting 16:00...")

while True:
    schedule.run_pending()
    time.sleep(1)

