"""
Data Fetcher Module
Shared utilities for fetching NAV data from Mutual Fund API

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

import requests
from datetime import datetime, timedelta
from typing import Dict, List

from config import API_SETTINGS


def fetch_nav_data(
    code: str,
    days: int = None,
    start_date: datetime = None,
    end_date: datetime = None
) -> List[Dict]:
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
        List of dictionaries with {date, nav} for each day
        
    Raises:
        requests.RequestException: If API call fails
        ValueError: If neither days nor start_date provided
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
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Build API URL and parameters
    api_url = f"{API_SETTINGS['base_url']}{code}"
    params = {
        'startDate': start_date_str,
        'endDate': end_date_str
    }
    
    # Fetch data from API
    response = requests.get(
        api_url,
        params=params,
        timeout=API_SETTINGS['timeout']
    )
    response.raise_for_status()
    
    data = response.json()
    
    # Parse NAV data
    nav_data = []
    for entry in data['data']:
        nav_data.append({
            'date': datetime.strptime(entry['date'], '%d-%m-%Y'),
            'nav': float(entry['nav'])
        })
    
    return nav_data


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
        requests.RequestException: If API call fails
    
    Example:
        >>> latest = fetch_latest_nav("120828")
        >>> print(f"NAV: {latest['nav']} on {latest['date']}")
    """
    api_url = f"{API_SETTINGS['base_url']}{code}/latest"
    
    response = requests.get(api_url, timeout=API_SETTINGS['timeout'])
    response.raise_for_status()
    
    data = response.json()
    
    # Parse and return the latest NAV data
    return {
        'date': datetime.strptime(data['data'][0]['date'], '%d-%m-%Y'),
        'nav': float(data['data'][0]['nav']),
        'fund_name': data.get('meta', {}).get('scheme_name', ''),
        'scheme_code': data.get('meta', {}).get('scheme_code', code)
    }


if __name__ == "__main__":
    # Test the data fetcher
    print("🧪 Testing Data Fetcher\n")
    
    test_code = "120828"  # Quant Small Cap
    
    # Test 1: Fetch latest NAV (fast)
    print("="*70)
    print("Test 1: Fetch Latest NAV (using /latest endpoint)")
    print("="*70)
    try:
        latest = fetch_latest_nav(test_code)
        print(f"✅ Latest NAV fetched successfully")
        print(f"   Fund: {latest['fund_name']}")
        print(f"   Date: {latest['date'].strftime('%d-%m-%Y')}")
        print(f"   NAV: ₹{latest['nav']:.2f}")
        print(f"   Code: {latest['scheme_code']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Fetch historical data
    print("\n" + "="*70)
    print("Test 2: Fetch Historical Data (30 days)")
    print("="*70)
    try:
        nav_data = fetch_nav_data(test_code, days=30)
        print(f"✅ Retrieved {len(nav_data)} days of data")
        print(f"   Latest: {nav_data[-1]['date'].strftime('%d-%m-%Y')} | NAV: ₹{nav_data[-1]['nav']:.2f}")
        print(f"   Oldest: {nav_data[0]['date'].strftime('%d-%m-%Y')} | NAV: ₹{nav_data[0]['nav']:.2f}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("💡 Tip: Use fetch_latest_nav() when you only need current NAV")
    print("   It's faster and uses less bandwidth!")
    print("="*70)

