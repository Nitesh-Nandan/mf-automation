import requests
from datetime import datetime, timedelta
from typing import Dict, Optional


def analyze_fund_dip(
    fund_name: str,
    code: str,
    dip_percentage: float = 10.0,
    days: int = 120
) -> Dict:
    """
    Analyze if a mutual fund's current NAV is in a dip compared to its peak.
    
    Args:
        fund_name: Name of the mutual fund
        code: API code for the fund
        dip_percentage: Percentage dip to check for (default: 10%)
        days: Number of days to look back for historical data (default: 90)
    
    Returns:
        Dictionary containing:
            - fund_name: Name of the fund
            - fund_code: API code
            - is_in_dip: Boolean indicating if current NAV is down by dip_percentage from peak
            - current_nav: Current NAV value
            - current_date: Date of current NAV
            - peak_nav: Peak NAV in the period
            - peak_date: Date when peak NAV occurred
            - mean_nav: Mean NAV over the period
            - dip_from_peak_percentage: Actual percentage dip from peak
            - days_analyzed: Number of days analyzed
            - error: Error message if any
    """
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates for API (ISO 8601 format: YYYY-MM-DD)
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Fetch data from API with date range parameters
        api_url = f"https://api.mfapi.in/mf/{code}"
        params = {
            'startDate': start_date_str,
            'endDate': end_date_str
        }
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if data is valid
        if 'data' not in data or not data['data']:
            return {
                'fund_name': fund_name,
                'fund_code': code,
                'error': 'No historical data available from API'
            }
        
        historical_data = data['data']
        
        # Parse the data
        filtered_data = []
        for entry in historical_data:
            entry_date = datetime.strptime(entry['date'], '%d-%m-%Y')
            filtered_data.append({
                'date': entry_date,
                'nav': float(entry['nav'])
            })
        
        if not filtered_data:
            return {
                'fund_name': fund_name,
                'fund_code': code,
                'error': f'No data available for the last {days} days'
            }
        
        # Sort by date (most recent first)
        filtered_data.sort(key=lambda x: x['date'], reverse=True)
        
        # Current NAV (most recent)
        current_nav = filtered_data[0]['nav']
        current_date = filtered_data[0]['date']
        
        # Find peak NAV and its date
        peak_entry = max(filtered_data, key=lambda x: x['nav'])
        peak_nav = peak_entry['nav']
        peak_date = peak_entry['date']
        
        # Calculate mean NAV
        mean_nav = sum(entry['nav'] for entry in filtered_data) / len(filtered_data)
        
        # Calculate dip percentage from peak
        dip_from_peak_percentage = ((peak_nav - current_nav) / peak_nav) * 100
        
        # Check if it's in a dip
        is_in_dip = dip_from_peak_percentage >= dip_percentage
        
        return {
            'fund_name': fund_name,
            'fund_code': code,
            'is_in_dip': is_in_dip,
            'current_nav': round(current_nav, 4),
            'current_date': current_date.strftime('%d-%m-%Y'),
            'peak_nav': round(peak_nav, 4),
            'peak_date': peak_date.strftime('%d-%m-%Y'),
            'mean_nav': round(mean_nav, 4),
            'dip_from_peak_percentage': round(dip_from_peak_percentage, 2),
            'days_analyzed': len(filtered_data),
            'error': None
        }
    
    except requests.RequestException as e:
        return {
            'fund_name': fund_name,
            'fund_code': code,
            'error': f'API request failed: {str(e)}'
        }
    except Exception as e:
        return {
            'fund_name': fund_name,
            'fund_code': code,
            'error': f'Error analyzing fund: {str(e)}'
        }


def print_analysis_result(result: Dict) -> None:
    """
    Pretty print the analysis result.
    
    Args:
        result: Dictionary returned from analyze_fund_dip
    """
    print("\n" + "="*70)
    print(f"Fund Analysis: {result['fund_name']}")
    print("="*70)
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"Fund Code: {result['fund_code']}")
    print(f"Days Analyzed: {result['days_analyzed']}")
    print(f"\nCurrent NAV: ₹{result['current_nav']} (as of {result['current_date']})")
    print(f"Peak NAV: ₹{result['peak_nav']} (on {result['peak_date']})")
    print(f"Mean NAV: ₹{result['mean_nav']}")
    print(f"\nDip from Peak: {result['dip_from_peak_percentage']}%")
    
    if result['is_in_dip']:
        print(f"✅ Fund is in a DIP (down {result['dip_from_peak_percentage']}% from peak)")
    else:
        print(f"❌ Fund is NOT in a significant dip (only {result['dip_from_peak_percentage']}% from peak)")
    
    print("="*70)


if __name__ == "__main__":
    # Example usage
    from mf_funds import get_mf_funds
    
    print("Loading mutual funds...")
    funds = get_mf_funds()
    
    # Analyze first fund as an example
    for fund in funds:
        first_fund = fund
        fund_name = first_fund['fund_name']
        fund_code = first_fund['code']
        
        if fund_code:
            print(f"\nAnalyzing: {fund_name}")
            result = analyze_fund_dip(
                fund_name=fund_name,
                code=fund_code,
                dip_percentage=10,
                days=200
            )
            print_analysis_result(result)
        else:
            print(f"No API code available for {fund_name}")

