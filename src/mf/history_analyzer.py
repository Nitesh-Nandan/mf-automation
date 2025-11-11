from datetime import datetime
from typing import Dict, List, Optional

from fund_loader import get_mf_funds
from data_fetcher import fetch_nav_data


def analyze_max_historical_dip(
    fund_name: str,
    code: str,
    days: int = 730,  # 2 years by default
    nav_data: Optional[List[Dict]] = None
) -> Dict:
    """
    Analyze the maximum NAV dip that has occurred historically for a fund.
    
    Args:
        fund_name: Name of the fund
        code: API code for the fund
        days: Number of days to look back (default: 730 = 2 years)
        nav_data: Optional pre-fetched NAV data (optimization to avoid duplicate API calls)
    
    Returns:
        Dictionary containing max dip information and when it occurred
    """
    
    try:
        # Use pre-fetched data if provided, otherwise fetch from API
        if nav_data is None:
            nav_data = fetch_nav_data(code, days=days)
        
        if len(nav_data) < 2:
            return {
                'fund_name': fund_name,
                'fund_code': code,
                'error': 'Not enough data'
            }
        
        # Data comes pre-sorted ASCENDING (oldest first) from dip_analyzer
        # For backward compatibility (standalone calls), ensure sorted
        if nav_data is None:
            nav_data.sort(key=lambda x: x['date'])
        
        # Calculate maximum dip by checking from each peak
        max_dip_percentage = 0
        max_dip_info = None
        
        # Track running maximum NAV and calculate dip from it
        running_max_nav = nav_data[0]['nav']
        running_max_date = nav_data[0]['date']
        
        for entry in nav_data:
            current_nav = entry['nav']
            current_date = entry['date']
            
            # Update running maximum
            if current_nav > running_max_nav:
                running_max_nav = current_nav
                running_max_date = current_date
            
            # Calculate dip from running maximum
            dip_percentage = ((running_max_nav - current_nav) / running_max_nav) * 100
            
            if dip_percentage > max_dip_percentage:
                max_dip_percentage = dip_percentage
                max_dip_info = {
                    'peak_nav': running_max_nav,
                    'peak_date': running_max_date,
                    'bottom_nav': current_nav,
                    'bottom_date': current_date,
                    'dip_percentage': dip_percentage
                }
        
        # Get current NAV info
        current_entry = nav_data[-1]
        current_nav = current_entry['nav']
        current_date = current_entry['date']
        
        # Find all-time peak in the period
        peak_entry = max(nav_data, key=lambda x: x['nav'])
        all_time_peak_nav = peak_entry['nav']
        all_time_peak_date = peak_entry['date']
        
        # Current dip from all-time peak
        current_dip = ((all_time_peak_nav - current_nav) / all_time_peak_nav) * 100
        
        return {
            'fund_name': fund_name,
            'fund_code': code,
            'days_analyzed': len(nav_data),
            'current_nav': round(current_nav, 4),
            'current_date': current_date.strftime('%d-%m-%Y'),
            'current_dip_from_peak': round(current_dip, 2),
            'all_time_peak_nav': round(all_time_peak_nav, 4),
            'all_time_peak_date': all_time_peak_date.strftime('%d-%m-%Y'),
            'max_historical_dip': round(max_dip_percentage, 2),
            'max_dip_details': {
                'peak_nav': round(max_dip_info['peak_nav'], 4),
                'peak_date': max_dip_info['peak_date'].strftime('%d-%m-%Y'),
                'bottom_nav': round(max_dip_info['bottom_nav'], 4),
                'bottom_date': max_dip_info['bottom_date'].strftime('%d-%m-%Y'),
                'dip_percentage': round(max_dip_info['dip_percentage'], 2)
            },
            'has_10_percent_dip': max_dip_percentage >= 10.0,
            'error': None
        }
    
    except Exception as e:
        return {
            'fund_name': fund_name,
            'fund_code': code,
            'error': f'Error: {str(e)}'
        }


def print_dip_analysis(result: Dict) -> None:
    """Pretty print the historical dip analysis."""
    print("\n" + "="*80)
    print(f"📊 Historical Dip Analysis: {result['fund_name']}")
    print("="*80)
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"Fund Code: {result['fund_code']}")
    print(f"Trading Days Analyzed: {result['days_analyzed']}")
    
    print(f"\n📈 Current Status:")
    print(f"  Current NAV: ₹{result['current_nav']} (as of {result['current_date']})")
    print(f"  All-Time Peak: ₹{result['all_time_peak_nav']} (on {result['all_time_peak_date']})")
    print(f"  Current Dip from Peak: {result['current_dip_from_peak']}%")
    
    print(f"\n📉 Maximum Historical Dip in Period:")
    max_dip = result['max_dip_details']
    print(f"  Dip Magnitude: {max_dip['dip_percentage']}%")
    print(f"  Peak NAV: ₹{max_dip['peak_nav']} (on {max_dip['peak_date']})")
    print(f"  Bottom NAV: ₹{max_dip['bottom_nav']} (on {max_dip['bottom_date']})")
    
    if result['has_10_percent_dip']:
        print(f"\n✅ YES - This fund HAS experienced a 10%+ dip historically!")
    else:
        print(f"\n❌ NO - This fund has NOT experienced a 10%+ dip in this period")
        print(f"   (Maximum dip was only {result['max_historical_dip']}%)")
    
    print("="*80)


if __name__ == "__main__":
    print("🔍 Analyzing Maximum Historical Dips for All Funds")
    print("Looking back 2 years (730 days) of trading history...")
    
    funds = get_mf_funds()
    
    results = []
    for fund in funds:
        fund_name = fund['fund_name']
        fund_code = fund['code']
        
        if fund_code:
            print(f"\nAnalyzing: {fund_name}...")
            result = analyze_max_historical_dip(
                fund_name=fund_name,
                code=fund_code,
                days=730  # 2 years
            )
            results.append(result)
            print_dip_analysis(result)
        else:
            print(f"\n⚠️  No API code available for {fund_name}")
    
    # Summary
    print("\n\n" + "="*80)
    print("📊 SUMMARY: Has 10%+ NAV Drop Ever Occurred?")
    print("="*80)
    
    funds_with_10_percent_dip = [r for r in results if r.get('has_10_percent_dip')]
    funds_without_10_percent_dip = [r for r in results if not r.get('has_10_percent_dip') and not r.get('error')]
    
    print(f"\n✅ Funds that HAVE experienced 10%+ dip: {len(funds_with_10_percent_dip)}")
    for r in funds_with_10_percent_dip:
        print(f"   • {r['fund_name']}: {r['max_historical_dip']}% max dip")
    
    print(f"\n❌ Funds that have NOT experienced 10%+ dip: {len(funds_without_10_percent_dip)}")
    for r in funds_without_10_percent_dip:
        print(f"   • {r['fund_name']}: {r['max_historical_dip']}% max dip")
    
    if funds_with_10_percent_dip:
        print(f"\n💡 Conclusion: 10% dip threshold is REALISTIC")
        print(f"   {len(funds_with_10_percent_dip)} out of {len(results)} funds have experienced such dips.")
    else:
        print(f"\n💡 Conclusion: 10% dip threshold might be too HIGH")
        print(f"   None of your funds experienced a 10%+ dip in the last 2 years.")
        if funds_without_10_percent_dip:
            max_observed = max(r['max_historical_dip'] for r in funds_without_10_percent_dip)
            print(f"   Maximum observed dip was {max_observed}%")
            print(f"   Consider a threshold between 5-7% for better sensitivity.")
    
    print("="*80)

