"""
Mutual Fund Dip Analyzer - Refactored
Clean, maintainable 6-factor algorithm for identifying optimal dip-buying opportunities
"""

from datetime import datetime
from typing import Dict, List

from mf_funds import get_mf_funds
from trends_analyser import analyze_fund_dip
from historical_dip_analysis import analyze_max_historical_dip
from scoring import calculate_all_scores
from data_fetcher import fetch_nav_data
from config import (
    TIME_WINDOWS,
    get_recommendation,
    RECOMMENDATION_THRESHOLDS
)


def analyze_dip_opportunity(
    fund_name: str,
    code: str,
    fund_type: str,
    analysis_days: int = None,
    historical_days: int = None,
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
        analysis_days: Lookback period for current analysis (default from config)
        historical_days: Lookback period for historical context (default from config)
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
    # Use config defaults if not specified
    if analysis_days is None:
        analysis_days = TIME_WINDOWS['current_analysis_days']
    if historical_days is None:
        historical_days = TIME_WINDOWS['historical_analysis_days']
    
    try:
        # Step 1: Get current dip analysis
        current_analysis = analyze_fund_dip(
            fund_name=fund_name,
            code=code,
            dip_percentage=TIME_WINDOWS['min_dip_threshold'],
            days=analysis_days
        )
        
        if current_analysis.get('error'):
            return {'error': current_analysis['error']}
        
        # Step 2: Get historical maximum dip
        historical_analysis = analyze_max_historical_dip(
            fund_name=fund_name,
            code=code,
            days=historical_days
        )
        
        if historical_analysis.get('error'):
            return {'error': historical_analysis['error']}
        
        # Step 3: Fetch full NAV data
        nav_data = fetch_nav_data(code, historical_days)
        
        # Step 4: Calculate all 6 factor scores
        score_breakdown, total_score = calculate_all_scores(
            current_analysis=current_analysis,
            historical_analysis=historical_analysis,
            nav_data=nav_data,
            fund_type=fund_type
        )
        
        # Step 5: Generate recommendation
        final_score = min(total_score, 100)
        triggers_buy, recommendation, allocation, confidence = get_recommendation(
            final_score,
            mode
        )
        
        # Step 6: Return complete analysis
        return {
            'fund_name': fund_name,
            'fund_code': code,
            'fund_type': fund_type,
            'total_score': round(final_score, 2),
            'recommendation': recommendation,
            'allocation_percentage': allocation,
            'confidence': confidence,
            'mode': mode,
            'threshold': RECOMMENDATION_THRESHOLDS.get(mode, RECOMMENDATION_THRESHOLDS['conservative']),
            'triggers_buy': triggers_buy,
            'score_breakdown': score_breakdown,
            'current_analysis': current_analysis,
            'historical_analysis': historical_analysis,
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
            score = result['total_score']
            rec = result['recommendation']
            print(f"  ✅ Score: {score:.1f} | {rec}")
        else:
            print(f"  ❌ {result['error']}")
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results


def print_analysis_summary(results: List[Dict], mode: str):
    """
    Print formatted summary of analysis results
    
    Args:
        results: List of analysis results
        mode: Analysis mode
    """
    threshold = RECOMMENDATION_THRESHOLDS.get(mode, RECOMMENDATION_THRESHOLDS['conservative'])
    
    print("\n" + "="*80)
    print("📊 DIP ANALYSIS SUMMARY")
    print("="*80)
    print(f"\nMode: {mode.upper()}")
    print(f"Threshold: {threshold} points")
    print(f"Funds analyzed: {len(results)}")
    
    buy_signals = [r for r in results if r['triggers_buy']]
    print(f"Buy signals triggered: {len(buy_signals)}")
    
    if buy_signals:
        print("\n🎯 BUY OPPORTUNITIES:")
        print("-"*80)
        print(f"{'Fund':40s} {'Score':>8s} {'Dip%':>8s} {'Rec':>15s} {'Alloc%':>8s}")
        print("-"*80)
        
        for result in buy_signals:
            fund = result['fund_name'][:38]
            score = result['total_score']
            dip = result['current_analysis']['dip_from_peak_percentage']
            rec = result['recommendation']
            alloc = result['allocation_percentage'] * 100
            
            print(f"{fund:40s} {score:>8.1f} {dip:>8.1f} {rec:>15s} {alloc:>7.0f}%")
    else:
        print("\n❌ No buy signals at this threshold")
    
    print("\n📈 TOP SCORING FUNDS:")
    print("-"*80)
    print(f"{'Fund':40s} {'Score':>8s} {'Dip%':>8s} {'Status':>15s}")
    print("-"*80)
    
    for result in results[:5]:  # Top 5
        fund = result['fund_name'][:38]
        score = result['total_score']
        dip = result['current_analysis']['dip_from_peak_percentage']
        rec = result['recommendation']
        
        print(f"{fund:40s} {score:>8.1f} {dip:>8.1f} {rec:>15s}")
    
    print("="*80)


def print_detailed_analysis(result: Dict):
    """
    Print detailed analysis for a single fund
    
    Args:
        result: Analysis result dictionary
    """
    print("\n" + "="*80)
    print(f"📊 DETAILED ANALYSIS: {result['fund_name']}")
    print("="*80)
    
    print(f"\n🎯 Overall Assessment:")
    print(f"  Total Score: {result['total_score']:.1f}/100")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Allocation: {result['allocation_percentage']*100:.0f}%")
    print(f"  Triggers Buy: {'✅ YES' if result['triggers_buy'] else '❌ NO'}")
    
    print(f"\n📈 Current Status:")
    curr = result['current_analysis']
    print(f"  Current NAV: ₹{curr['current_nav']:.2f}")
    print(f"  Peak NAV: ₹{curr['peak_nav']:.2f}")
    print(f"  Mean NAV: ₹{curr['mean_nav']:.2f}")
    print(f"  Dip from Peak: {curr['dip_from_peak_percentage']:.2f}%")
    
    print(f"\n🔍 Historical Context:")
    hist = result['historical_analysis']
    print(f"  Max Historical Dip: {hist['max_historical_dip']:.2f}%")
    print(f"  Peak Date: {hist['peak_date']}")
    print(f"  Bottom Date: {hist['bottom_date']}")
    
    print(f"\n⭐ Score Breakdown:")
    for factor_name, factor_data in result['score_breakdown'].items():
        score = factor_data['score']
        max_score = factor_data['max']
        factor = factor_data.get('factor', factor_name.replace('_', ' ').title())
        print(f"  {factor:20s}: {score:5.1f}/{max_score} pts")
    
    print("="*80)


if __name__ == "__main__":
    import sys
    
    print("🚀 MUTUAL FUND DIP ANALYZER")
    print("="*80)
    print("Comprehensive 6-factor analysis for optimal entry points")
    print("="*80)
    
    # Parse command line arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else 'conservative'
    
    # Validate mode
    if mode not in RECOMMENDATION_THRESHOLDS:
        print(f"❌ Invalid mode: {mode}")
        print(f"Valid modes: {', '.join(RECOMMENDATION_THRESHOLDS.keys())}")
        sys.exit(1)
    
    # Run analysis
    results = analyze_all_funds(mode=mode)
    
    # Print summary
    print_analysis_summary(results, mode)
    
    # Print detailed analysis for top fund if any
    if results and results[0]['triggers_buy']:
        print("\n")
        print_detailed_analysis(results[0])

