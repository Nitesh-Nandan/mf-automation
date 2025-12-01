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


def get_historical_data(
    instrument_key, to_date, from_date, unit=IntervalUnit.DAYS, interval="1"
):
    """
    Fetch historical candle data from Upstox API

    Args:
        instrument_key: Upstox instrument key (e.g., "NSE_EQ|INE021A01026")
        to_date: End date in YYYY-MM-DD format
        from_date: Start date in YYYY-MM-DD format
        unit: IntervalUnit enum (DAYS, WEEKS, MONTHS)
        interval: Interval value (e.g., "1" for 1 day)

    Returns:
        Dictionary with candle data or None on error
        Format: {'status': 'success', 'data': {'candles': [[timestamp, o, h, l, c, v, oi], ...]}}
    """
    # URL encode instrument_key (e.g. NSE_EQ|... -> NSE_EQ%7C...)
    encoded_key = quote(instrument_key)

    # url format: https://api.upstox.com/v3/historical-candle/{instrument_key}/{unit}/{interval}/{to_date}/{from_date}
    url = f"https://api.upstox.com/v3/historical-candle/{encoded_key}/{unit.value}/{interval}/{to_date}/{from_date}"

    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        print("Error: UPSTOX_ACCESS_TOKEN not found in environment variables.")
        return None

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_ltp(instrument_key):
    """
    Get Last Traded Price for an instrument

    Args:
        instrument_key: Upstox instrument key (e.g., "NSE_EQ|INE021A01026")

    Returns:
        Dictionary with LTP data or None on error
        Format: {'status': 'success', 'data': {instrument_key: {'last_price': 1234.56}}}
    """
    # URL encode instrument_key
    encoded_key = quote(instrument_key)

    url = f"https://api.upstox.com/v3/market-quote/ltp?instrument_key={encoded_key}"

    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        print("Error: UPSTOX_ACCESS_TOKEN not found in environment variables.")
        return None

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


if __name__ == "__main__":
    # Example usage
    instrument_key = "NSE_EQ|INE848E01016"

    historical_data = get_historical_data(instrument_key, "2025-03-01", "2023-01-01")
    ltp_data = get_ltp(instrument_key)

    if historical_data and ltp_data:
        print("✓ API test successful")

    print(ltp_data)
