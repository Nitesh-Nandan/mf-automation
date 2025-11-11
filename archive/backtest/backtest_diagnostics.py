"""
Diagnostic tool to understand why buy signals weren't triggered
Shows score history and identifies best potential entry points
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List
import statistics
from mf_funds import get_mf_funds


def fetch_historical_data(code: str, days: int = 1095) -> List[Dict]:
    """Fetch historical data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    api_url = f"https://api.mfapi.in/mf/{code}"
    params = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d')
    }
    
    response = requests.get(api_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    nav_data = []
    for entry in data['data']:
        nav_data.append({
            'date': datetime.strptime(entry['date'], '%d-%m-%Y'),
            'nav': float(entry['nav'])
        })
    
    return sorted(nav_data, key=lambda x: x['date'])


def calculate_score_at_point(nav_data: List[Dict], current_index: int) -> Dict:
    """Calculate algorithm score at a specific point in time"""
    current_date = nav_data[current_index]['date']
    current_nav = nav_data[current_index]['nav']
    
    # Get recent data (120 days)
    analysis_start = current_date - timedelta(days=120)
    recent_data = [d for d in nav_data[:current_index+1] 
                   if d['date'] >= analysis_start]
    
    # Get historical data (730 days)
    historical_start = current_date - timedelta(days=730)
    historical_data = [d for d in nav_data[:current_index+1] 
                       if d['date'] >= historical_start]
    
    if len(recent_data) < 30 or len(historical_data) < 100:
        return None
    
    # Factor 1: Dip Depth
    peak_entry = max(recent_data, key=lambda x: x['nav'])
    peak_nav = peak_entry['nav']
    dip_percentage = ((peak_nav - current_nav) / peak_nav) * 100
    
    if dip_percentage >= 20:
        dip_score = 25
    elif dip_percentage >= 15:
        dip_score = 22
    elif dip_percentage >= 12:
        dip_score = 18
    elif dip_percentage >= 10:
        dip_score = 15
    elif dip_percentage >= 7:
        dip_score = 10
    elif dip_percentage >= 5:
        dip_score = 5
    else:
        dip_score = 0
    
    # Factor 2: Historical Context
    max_historical_dip = 0
    running_max = historical_data[0]['nav']
    for entry in historical_data:
        if entry['nav'] > running_max:
            running_max = entry['nav']
        dip = ((running_max - entry['nav']) / running_max) * 100
        if dip > max_historical_dip:
            max_historical_dip = dip
    
    if max_historical_dip > 0:
        dip_ratio = (dip_percentage / max_historical_dip) * 100
        if 60 <= dip_ratio <= 80:
            historical_score = 20
        elif 80 < dip_ratio <= 90:
            historical_score = 18
        elif 50 <= dip_ratio < 60:
            historical_score = 15
        elif 40 <= dip_ratio < 50:
            historical_score = 10
        elif dip_ratio > 90:
            historical_score = 12
        else:
            historical_score = 5
    else:
        historical_score = 10
    
    # Factor 3: Mean Reversion
    mean_nav = sum(d['nav'] for d in recent_data) / len(recent_data)
    if current_nav < mean_nav:
        deviation = ((mean_nav - current_nav) / mean_nav) * 100
        mean_score = min(deviation * 2, 15)
    else:
        mean_score = 0
    
    # Factor 4: Volatility
    returns = [(historical_data[i]['nav'] - historical_data[i-1]['nav']) / historical_data[i-1]['nav']
               for i in range(1, len(historical_data))]
    volatility = statistics.stdev(returns) * (252 ** 0.5) * 100 if len(returns) > 1 else 0
    
    if 15 <= volatility <= 25:
        volatility_score = 15
    elif 25 < volatility <= 35:
        volatility_score = 12
    elif 10 <= volatility < 15:
        volatility_score = 10
    elif volatility > 35:
        volatility_score = 5
    else:
        volatility_score = 3
    
    recovery_score = 10
    type_score = 10
    
    total_score = dip_score + historical_score + mean_score + volatility_score + recovery_score + type_score
    
    return {
        'date': current_date,
        'nav': current_nav,
        'score': total_score,
        'dip_percentage': dip_percentage,
        'dip_score': dip_score,
        'historical_score': historical_score,
        'mean_score': mean_score,
        'volatility_score': volatility_score,
        'peak_nav': peak_nav,
        'max_historical_dip': max_historical_dip
    }


def analyze_score_history(fund_name: str, code: str, analysis_days: int = 365):
    """Analyze score history to understand algorithm behavior"""
    
    print(f"\n{'='*80}")
    print(f"📊 SCORE HISTORY ANALYSIS: {fund_name}")
    print(f"{'='*80}")
    
    # Fetch data
    nav_data = fetch_historical_data(code, days=1095)
    
    # Analyze last year
    analysis_start = datetime.now() - timedelta(days=analysis_days)
    analysis_indices = [i for i, d in enumerate(nav_data) if d['date'] >= analysis_start]
    
    if not analysis_indices:
        print("❌ No data available")
        return
    
    # Calculate scores every 7 days
    score_history = []
    for i in range(0, len(analysis_indices), 7):
        idx = analysis_indices[i]
        if idx >= 730:  # Need enough history
            result = calculate_score_at_point(nav_data, idx)
            if result:
                score_history.append(result)
    
    if not score_history:
        print("❌ Insufficient data for analysis")
        return
    
    # Statistics
    max_score_entry = max(score_history, key=lambda x: x['score'])
    min_score_entry = min(score_history, key=lambda x: x['score'])
    avg_score = sum(s['score'] for s in score_history) / len(score_history)
    
    buy_signals = [s for s in score_history if s['score'] >= 60]
    moderate_signals = [s for s in score_history if 45 <= s['score'] < 60]
    
    print(f"\n📈 Score Statistics (last {analysis_days} days):")
    print(f"  Average Score:        {avg_score:.2f}")
    print(f"  Maximum Score:        {max_score_entry['score']:.2f} (on {max_score_entry['date'].strftime('%d-%m-%Y')})")
    print(f"  Minimum Score:        {min_score_entry['score']:.2f}")
    print(f"  Buy Signals (>=60):   {len(buy_signals)}")
    print(f"  Moderate (45-59):     {len(moderate_signals)}")
    
    # Show top 5 scoring opportunities
    print(f"\n🎯 TOP 5 SCORING OPPORTUNITIES (Best entry points):")
    print(f"{'Date':<12} {'Score':<7} {'NAV':<10} {'Dip%':<7} {'Return if bought':<15}")
    print("-"*80)
    
    top_opportunities = sorted(score_history, key=lambda x: x['score'], reverse=True)[:5]
    current_nav = nav_data[-1]['nav']
    
    for opp in top_opportunities:
        potential_return = ((current_nav - opp['nav']) / opp['nav']) * 100
        print(f"{opp['date'].strftime('%d-%m-%Y'):<12} "
              f"{opp['score']:<7.1f} "
              f"₹{opp['nav']:<9.2f} "
              f"{opp['dip_percentage']:<7.2f} "
              f"{potential_return:+.2f}%")
    
    # Factor breakdown for best opportunity
    if top_opportunities:
        best = top_opportunities[0]
        print(f"\n🔍 FACTOR BREAKDOWN (Best opportunity on {best['date'].strftime('%d-%m-%Y')}):")
        print(f"  Dip Depth:           {best['dip_score']}/25 (dip: {best['dip_percentage']:.2f}%)")
        print(f"  Historical Context:  {best['historical_score']}/20 (max historical: {best['max_historical_dip']:.2f}%)")
        print(f"  Mean Reversion:      {best['mean_score']:.2f}/15")
        print(f"  Volatility:          {best['volatility_score']}/15")
        print(f"  Recovery:            10/15 (neutral)")
        print(f"  Fund Type:           10/10")
    
    # Recommendation
    print(f"\n💡 INSIGHTS:")
    if avg_score < 40:
        print(f"  ⚠️  Average score ({avg_score:.1f}) is very low - fund has been bullish")
        print(f"  ⚠️  No significant dips occurred in this period")
        print(f"  💡 Consider lowering threshold to 45-50 for this market condition")
    elif avg_score < 50:
        print(f"  ℹ️  Average score ({avg_score:.1f}) is below buy threshold")
        print(f"  💡 Market was relatively stable, few dip opportunities")
    else:
        print(f"  ✅ Good dip opportunities were present (avg score: {avg_score:.1f})")
    
    if len(buy_signals) == 0:
        print(f"  ❌ Zero buy signals in {analysis_days} days - threshold too high!")
        if max_score_entry['score'] >= 50:
            print(f"  💡 Best score was {max_score_entry['score']:.1f} - consider threshold of 50")
    
    print("="*80)


def diagnose_all_funds():
    """Run diagnostics on all funds"""
    funds = get_mf_funds()
    
    print("\n" + "🔬 " + "="*78)
    print("ALGORITHM DIAGNOSTICS - Score History Analysis")
    print("="*80)
    
    for fund in funds:
        if not fund.get('code'):
            continue
        
        try:
            analyze_score_history(fund['fund_name'], fund['code'], analysis_days=365)
        except Exception as e:
            print(f"\n❌ Error analyzing {fund['fund_name']}: {str(e)}")
    
    print("\n" + "="*80)
    print("🎯 OVERALL RECOMMENDATION")
    print("="*80)
    print("Based on the analysis above:")
    print("1. If most funds show avg score < 40: Market was bullish, consider threshold of 45-50")
    print("2. If max scores are 55-65: Threshold of 60 is appropriate but may miss some opportunities")
    print("3. If buy signals occurred: Algorithm is working, just waiting for right conditions")
    print("4. Consider adding a 'relaxed mode' with lower threshold for less volatile periods")
    print("="*80)


if __name__ == "__main__":
    diagnose_all_funds()

