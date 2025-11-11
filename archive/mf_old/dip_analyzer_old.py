"""
Mutual Fund Dip Analyzer - Production Ready
A robust 6-factor algorithm for identifying optimal dip-buying opportunities
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List
import statistics
from mf_funds import get_mf_funds
from trends_analyser import analyze_fund_dip
from historical_dip_analysis import analyze_max_historical_dip


def calculate_volatility(nav_data: List[Dict]) -> float:
    """
    Calculate annualized volatility of NAV returns
    
    Formula: Standard Deviation of Daily Returns × √252 × 100
    Where 252 = typical trading days per year
    
    Returns:
        Annualized volatility as percentage
    """
    if len(nav_data) < 2:
        return 0.0
    
    returns = []
    for i in range(1, len(nav_data)):
        daily_return = (nav_data[i]['nav'] - nav_data[i-1]['nav']) / nav_data[i-1]['nav']
        returns.append(daily_return)
    
    if not returns:
        return 0.0
    
    volatility = statistics.stdev(returns) * (252 ** 0.5) * 100
    return volatility


def calculate_recovery_speed(nav_data: List[Dict]) -> Dict:
    """
    Analyze historical recovery speed from dips
    
    Tracks all 5%+ dips and measures days to full recovery
    
    Returns:
        Dictionary with average recovery days and count
    """
    nav_data_sorted = sorted(nav_data, key=lambda x: x['date'])
    
    recoveries = []
    in_dip = False
    dip_start_idx = 0
    peak_nav = nav_data_sorted[0]['nav']
    
    for i, entry in enumerate(nav_data_sorted):
        current_nav = entry['nav']
        
        if current_nav > peak_nav:
            if in_dip and i > dip_start_idx:
                recovery_days = (entry['date'] - nav_data_sorted[dip_start_idx]['date']).days
                recoveries.append(recovery_days)
                in_dip = False
            peak_nav = current_nav
        
        dip_pct = ((peak_nav - current_nav) / peak_nav) * 100
        if dip_pct >= 5 and not in_dip:
            in_dip = True
            dip_start_idx = i
    
    if recoveries:
        avg_recovery = sum(recoveries) / len(recoveries)
        return {
            'avg_recovery_days': avg_recovery,
            'recovery_count': len(recoveries),
            'has_history': True
        }
    
    return {'avg_recovery_days': 0, 'recovery_count': 0, 'has_history': False}


def analyze_dip_opportunity(
    fund_name: str,
    code: str,
    fund_type: str,
    analysis_days: int = 120,
    historical_days: int = 730,
    mode: str = 'conservative'
) -> Dict:
    """
    Comprehensive 6-factor dip-buying analysis
    
    Calculates a 0-100 score based on:
    1. Dip Depth (0-25 pts) - How far from peak
    2. Historical Context (0-20 pts) - Compared to past dips
    3. Mean Reversion (0-15 pts) - Below average price
    4. Volatility (0-15 pts) - Risk/reward balance
    5. Recovery Speed (0-15 pts) - Historical resilience
    6. Fund Type (0-10 pts) - Category adjustment
    
    Args:
        fund_name: Name of the mutual fund
        code: API code for the fund
        fund_type: Category (Small Cap, Mid Cap, Large Cap, etc.)
        analysis_days: Lookback period for current analysis (default: 120)
        historical_days: Lookback period for historical context (default: 730)
        mode: Risk level - 'ultra_conservative', 'conservative', 'moderate', 'aggressive'
    
    Returns:
        Dictionary containing:
        - total_score: 0-100 overall score
        - recommendation: STRONG BUY, BUY, MODERATE BUY, WEAK BUY, or HOLD
        - triggers_buy: Boolean if score meets threshold
        - allocation_percentage: Suggested capital allocation
        - score_breakdown: Individual factor scores
        - Full analysis details
    """
    
    try:
        # Get current dip analysis (120-day window)
        current_analysis = analyze_fund_dip(
            fund_name=fund_name,
            code=code,
            dip_percentage=5,
            days=analysis_days
        )
        
        if current_analysis.get('error'):
            return {'error': current_analysis['error']}
        
        # Get historical maximum dip (730-day window)
        historical_analysis = analyze_max_historical_dip(
            fund_name=fund_name,
            code=code,
            days=historical_days
        )
        
        if historical_analysis.get('error'):
            return {'error': historical_analysis['error']}
        
        # Fetch full NAV data for volatility and recovery calculations
        end_date = datetime.now()
        start_date = end_date - timedelta(days=historical_days)
        
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
        
        # === CALCULATE ALL 6 FACTORS ===
        
        score_breakdown = {}
        total_score = 0
        
        # FACTOR 1: Dip Depth (0-25 points)
        # Deeper dips score higher (bigger discount)
        current_dip = current_analysis['dip_from_peak_percentage']
        if current_dip >= 20:
            dip_score = 25
        elif current_dip >= 15:
            dip_score = 22
        elif current_dip >= 12:
            dip_score = 18
        elif current_dip >= 10:
            dip_score = 15
        elif current_dip >= 7:
            dip_score = 10
        elif current_dip >= 5:
            dip_score = 5
        else:
            dip_score = 0
        
        score_breakdown['dip_depth'] = {
            'score': dip_score,
            'value': current_dip,
            'max': 25
        }
        total_score += dip_score
        
        # FACTOR 2: Historical Context (0-20 points)
        # Sweet spot: 60-80% of maximum historical dip
        max_historical_dip = historical_analysis['max_historical_dip']
        if max_historical_dip > 0:
            dip_ratio = (current_dip / max_historical_dip) * 100
            
            if 60 <= dip_ratio <= 80:
                historical_score = 20  # Optimal range
            elif 80 < dip_ratio <= 90:
                historical_score = 18
            elif 50 <= dip_ratio < 60:
                historical_score = 15
            elif 40 <= dip_ratio < 50:
                historical_score = 10
            elif dip_ratio > 90:
                historical_score = 12  # Near maximum, caution
            else:
                historical_score = 5
        else:
            historical_score = 10  # Neutral if no historical data
        
        score_breakdown['historical_context'] = {
            'score': historical_score,
            'current_vs_max_ratio': round(dip_ratio, 2) if max_historical_dip > 0 else 0,
            'max': 20
        }
        total_score += historical_score
        
        # FACTOR 3: Mean Reversion (0-15 points)
        # Scores when price is below average (statistical pull back expected)
        current_nav = current_analysis['current_nav']
        mean_nav = current_analysis['mean_nav']
        
        if current_nav < mean_nav:
            deviation = ((mean_nav - current_nav) / mean_nav) * 100
            mean_score = min(deviation * 2, 15)  # 2 points per 1% below mean
        else:
            mean_score = 0  # No points if above mean
        
        score_breakdown['mean_reversion'] = {
            'score': round(mean_score, 2),
            'below_mean_pct': round(((mean_nav - current_nav) / mean_nav) * 100, 2),
            'max': 15
        }
        total_score += mean_score
        
        # FACTOR 4: Volatility (0-15 points)
        # Goldilocks zone: 15-25% volatility (good movement, manageable risk)
        volatility = calculate_volatility(nav_data)
        
        if 15 <= volatility <= 25:
            volatility_score = 15  # Sweet spot
        elif 25 < volatility <= 35:
            volatility_score = 12
        elif 10 <= volatility < 15:
            volatility_score = 10
        elif volatility > 35:
            volatility_score = 5  # Too risky
        else:
            volatility_score = 3  # Too stable
        
        score_breakdown['volatility'] = {
            'score': volatility_score,
            'value': round(volatility, 2),
            'max': 15
        }
        total_score += volatility_score
        
        # FACTOR 5: Recovery Track Record (0-15 points)
        # Faster recovery = better score
        recovery_stats = calculate_recovery_speed(nav_data)
        
        if recovery_stats['has_history']:
            avg_recovery = recovery_stats['avg_recovery_days']
            
            if avg_recovery <= 30:
                recovery_score = 15  # Quick recovery
            elif avg_recovery <= 60:
                recovery_score = 12
            elif avg_recovery <= 90:
                recovery_score = 8
            else:
                recovery_score = 4  # Slow recovery
        else:
            recovery_score = 8  # Neutral if no history
        
        score_breakdown['recovery_track_record'] = {
            'score': recovery_score,
            'avg_recovery_days': recovery_stats.get('avg_recovery_days', 0),
            'recovery_count': recovery_stats.get('recovery_count', 0),
            'max': 15
        }
        total_score += recovery_score
        
        # FACTOR 6: Fund Type (0-10 points)
        # Higher risk categories get bonus (higher growth potential)
        fund_type_scores = {
            'Small Cap': 10,   # Highest growth potential
            'Flexi Cap': 8,
            'Mid Cap': 8,
            'Large Cap': 6,    # Lower volatility, lower opportunity
            'Debt': 3,
        }
        
        type_score = fund_type_scores.get(fund_type, 7)  # Default 7
        
        score_breakdown['fund_type'] = {
            'score': type_score,
            'type': fund_type,
            'max': 10
        }
        total_score += type_score
        
        # === GENERATE RECOMMENDATION ===
        
        # Mode-based thresholds
        thresholds = {
            'ultra_conservative': 70,  # Only extreme dips
            'conservative': 60,        # Significant dips (default)
            'moderate': 50,            # Moderate pullbacks
            'aggressive': 40           # Any dip
        }
        
        threshold = thresholds.get(mode, 60)
        final_score = min(total_score, 100)
        
        # Recommendation and allocation based on score
        if final_score >= 75:
            recommendation = 'STRONG BUY'
            allocation = 0.40  # 40% of available capital
            confidence = 'Very High'
        elif final_score >= 60:
            recommendation = 'BUY'
            allocation = 0.30  # 30%
            confidence = 'High'
        elif final_score >= 45:
            recommendation = 'MODERATE BUY'
            allocation = 0.20  # 20%
            confidence = 'Medium'
        elif final_score >= 30:
            recommendation = 'WEAK BUY'
            allocation = 0.10  # 10%
            confidence = 'Low'
        else:
            recommendation = 'HOLD'
            allocation = 0.0  # 0%
            confidence = 'None'
        
        # Check if score meets mode threshold
        triggers_buy = final_score >= threshold
        
        return {
            'fund_name': fund_name,
            'fund_code': code,
            'fund_type': fund_type,
            'total_score': round(final_score, 2),
            'recommendation': recommendation,
            'allocation_percentage': allocation,
            'confidence': confidence,
            'mode': mode,
            'threshold': threshold,
            'triggers_buy': triggers_buy,
            'score_breakdown': score_breakdown,
            'current_analysis': current_analysis,
            'historical_analysis': historical_analysis,
            'volatility': round(volatility, 2),
            'error': None
        }
        
    except Exception as e:
        return {
            'fund_name': fund_name,
            'fund_code': code,
            'error': f'Error: {str(e)}'
        }


def analyze_all_funds(mode: str = 'conservative') -> List[Dict]:
    """
    Analyze all funds from mf_funds.csv
    
    Args:
        mode: Risk level ('ultra_conservative', 'conservative', 'moderate', 'aggressive')
    
    Returns:
        List of analysis results sorted by score (highest first)
    """
    funds = get_mf_funds()
    results = []
    
    print(f"\n🎯 Analyzing Dip Opportunities - {mode.upper()} MODE")
    print("="*80)
    
    for fund in funds:
        if not fund.get('code'):
            print(f"⚠️  Skipping {fund['fund_name']} - No API code")
            continue
        
        print(f"Analyzing {fund['fund_name']}...")
        
        result = analyze_dip_opportunity(
            fund_name=fund['fund_name'],
            code=fund['code'],
            fund_type=fund['type'],
            mode=mode
        )
        
        if not result.get('error'):
            results.append(result)
        else:
            print(f"  ❌ Error: {result['error']}")
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results


def print_analysis_summary(results: List[Dict], mode: str):
    """Print formatted summary of analysis results"""
    print("\n" + "="*80)
    print(f"📊 ANALYSIS SUMMARY - {mode.upper()} MODE")
    print("="*80)
    
    if not results:
        print("No results to display")
        return
    
    buy_triggered = [r for r in results if r['triggers_buy']]
    
    print(f"\nThreshold: {results[0]['threshold']} points")
    print(f"Funds analyzed: {len(results)}")
    print(f"Buy signals triggered: {len(buy_triggered)}")
    
    if buy_triggered:
        print(f"\n✅ FUNDS TO BUY:")
        print(f"{'Fund Name':<50} {'Score':<8} {'Recommendation':<15} {'Allocate':<10}")
        print("-"*80)
        for r in buy_triggered:
            alloc_pct = f"{r['allocation_percentage']*100:.0f}%"
            print(f"{r['fund_name']:<50} {r['total_score']:<8.1f} {r['recommendation']:<15} {alloc_pct:<10}")
    else:
        print(f"\n❌ No buy signals at this threshold")
        print(f"\n📊 Top scoring opportunities:")
        print(f"{'Fund Name':<50} {'Score':<8} {'Status':<15}")
        print("-"*80)
        for r in results[:5]:
            print(f"{r['fund_name']:<50} {r['total_score']:<8.1f} {r['recommendation']:<15}")
    
    print("="*80)


if __name__ == "__main__":
    """
    Usage: python dip_analyzer.py
    
    Analyzes all funds in multiple modes to identify best buying opportunities
    """
    print("🚀 MUTUAL FUND DIP ANALYZER")
    print("="*80)
    print("Comprehensive 6-factor analysis for optimal entry points")
    print("="*80)
    
    # Analyze in multiple modes
    for mode in ['conservative', 'moderate']:
        results = analyze_all_funds(mode=mode)
        print_analysis_summary(results, mode)
        print("\n")
    
    print("💡 TIP: Use 'conservative' mode for regular dip-buying")
    print("💡 TIP: Use 'moderate' mode during bull markets for more opportunities")
    print("="*80)

