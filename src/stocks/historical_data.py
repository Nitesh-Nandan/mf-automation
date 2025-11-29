import requests
import os
from urllib.parse import quote
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class IntervalUnit(str, Enum):
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"


def get_historical_data(instrument_key, to_date, from_date, unit=IntervalUnit.DAYS, interval="1"):
    # URL encode instrument_key (e.g. NSE_EQ|... -> NSE_EQ%7C...)
    encoded_key = quote(instrument_key)
    
    # url format: https://api.upstox.com/v3/historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}
    url = f'https://api.upstox.com/v3/historical-candle/{encoded_key}/{unit.value}/{interval}/{to_date}/{from_date}'
    
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        print("Error: UPSTOX_ACCESS_TOKEN not found in environment variables.")
        return

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")


def get_ltp(instrument_key):
    # URL encode instrument_key
    encoded_key = quote(instrument_key)
    
    url = f'https://api.upstox.com/v3/market-quote/ltp?instrument_key={encoded_key}'
    
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        print("Error: UPSTOX_ACCESS_TOKEN not found in environment variables.")
        return

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    instrument_key = "NSE_EQ|INE848E01016"
    # Example usage with enum: IntervalUnit.DAYS.value returns "days"
    get_historical_data(instrument_key, "2025-03-01", "2025-01-01")
    
    # Get LTP
    get_ltp(instrument_key)