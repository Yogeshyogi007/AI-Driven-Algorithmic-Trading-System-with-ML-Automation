import schedule
import time

def run_trading_bot():
    exec(open("live_trading.py").read())

schedule.every().day.at("09:15").do(run_trading_bot)  # Adjust time as needed

while True:
    schedule.run_pending()
    time.sleep(60)
