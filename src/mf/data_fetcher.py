"""
Data Fetcher Module

Shared utilities for fetching NAV data from Mutual Fund API.

API Endpoints:
--------------
1. Historical Data: https://api.mfapi.in/mf/{code}
   - Returns all historical NAV data
   - Supports startDate & endDate parameters for filtering
   - Use for: Trend analysis, dip detection, historical comparisons

2. Latest NAV: https://api.mfapi.in/mf/{code}/latest
   - Returns only the most recent NAV
   - Much faster and more efficient
   - Use for: Current price checks, quick lookups

Usage Guide:
-----------
- Use fetch_latest_nav() when you only need the current NAV
- Use fetch_nav_data() when you need historical analysis
- Both functions handle date parsing and type conversion automatically
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

from .config import API_SETTINGS
from .constants import DATE_FORMAT_API, DATE_FORMAT_ISO
from .exceptions import DataFetchError
from .types import NAVEntry


def fetch_nav_data(
    code: str,
    days: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[NAVEntry]:
    """
    Fetch NAV data from Mutual Fund API

    Can specify either:
    - days: Number of days to fetch (from today backwards)
    - start_date & end_date: Explicit date range

    Args:
        code: Mutual fund API code
        days: Number of days to fetch (optional)
        start_date: Start date for data (optional)
        end_date: End date for data (optional, defaults to today)

    Returns:
        List of NAV entries with date and nav fields

    Raises:
        DataFetchError: If API call fails
        ValueError: If neither days nor start_date provided

    Example:
        >>> nav_data = fetch_nav_data("120828", days=30)
        >>> print(f"Fetched {len(nav_data)} days of data")
    """
    # Determine date range
    if days is not None:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
    elif start_date is None:
        raise ValueError("Must provide either 'days' or 'start_date'")

    if end_date is None:
        end_date = datetime.now()

    # Format dates for API (ISO 8601 format: YYYY-MM-DD)
    start_date_str = start_date.strftime(DATE_FORMAT_ISO)
    end_date_str = end_date.strftime(DATE_FORMAT_ISO)

    # Build API URL and parameters
    api_url = f"{API_SETTINGS['base_url']}{code}"
    params = {"startDate": start_date_str, "endDate": end_date_str}

    try:
        # Fetch data from API
        response = requests.get(api_url, params=params, timeout=API_SETTINGS["timeout"])
        response.raise_for_status()

        data = response.json()

        # Parse NAV data
        nav_data: List[NAVEntry] = []
        for entry in data["data"]:
            nav_data.append(
                {
                    "date": datetime.strptime(entry["date"], DATE_FORMAT_API),
                    "nav": float(entry["nav"]),
                }
            )

        return nav_data

    except requests.RequestException as e:
        raise DataFetchError(code, f"Failed to fetch NAV data: {str(e)}")
    except (KeyError, ValueError) as e:
        raise DataFetchError(code, f"Failed to parse NAV data: {str(e)}")


def fetch_latest_nav(code: str) -> Dict:
    """
    Fetch only the latest NAV using the dedicated /latest endpoint

    This is much faster and more efficient than fetching historical data
    when you only need the current NAV.

    Args:
        code: Mutual fund API code

    Returns:
        Dictionary with {date, nav, fund_name, scheme_code}

    Raises:
        DataFetchError: If API call fails

    Example:
        >>> latest = fetch_latest_nav("120828")
        >>> print(f"NAV: {latest['nav']} on {latest['date']}")
    """
    api_url = f"{API_SETTINGS['base_url']}{code}/latest"

    try:
        response = requests.get(api_url, timeout=API_SETTINGS["timeout"])
        response.raise_for_status()

        data = response.json()

        # Parse and return the latest NAV data
        return {
            "date": datetime.strptime(data["data"][0]["date"], DATE_FORMAT_API),
            "nav": float(data["data"][0]["nav"]),
            "fund_name": data.get("meta", {}).get("scheme_name", ""),
            "scheme_code": data.get("meta", {}).get("scheme_code", code),
        }

    except requests.RequestException as e:
        raise DataFetchError(code, f"Failed to fetch latest NAV: {str(e)}")
    except (KeyError, ValueError, IndexError) as e:
        raise DataFetchError(code, f"Failed to parse latest NAV: {str(e)}")
