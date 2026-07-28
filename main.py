from booking import run_booking_script
import time
import schedule

def run_job():
    print("Executing class booking")
    run_booking_script()

schedule.every().sunday.at("16:00").do(run_job)
schedule.every().sunday.at("17:00").do(run_job)

schedule.every().monday.at("16:00").do(run_job)
schedule.every().monday.at("17:00").do(run_job)

schedule.every().tuesday.at("16:00").do(run_job)
schedule.every().tuesday.at("17:00").do(run_job)

schedule.every().thursday.at("16:00").do(run_job)
schedule.every().thursday.at("17:00").do(run_job)

schedule.every().friday.at("09:00").do(run_job)

print("Booking bot initiated. Awaiting 16:00...")

while True:
    schedule.run_pending()
    time.sleep(60)

