import requests
from datetime import datetime, timedelta
from typing import Dict, List
import statistics
from mf_funds import get_mf_funds


def fetch_full_historical_data(code: str, days: int = 1095) -> List[Dict]:
    """Fetch 3 years of historical data for backtesting"""
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


def simulate_algorithm_at_point_in_time(
    nav_data: List[Dict],
    current_index: int,
    lookback_days: int = 120,
    historical_days: int = 730
) -> Dict:
    """
    Simulate what the algorithm would have scored at a specific point in time
    Uses only data available UP TO that point (no future peeking!)
    """
    current_date = nav_data[current_index]['date']
    current_nav = nav_data[current_index]['nav']
    
    # Get data available at this point in time
    analysis_start = current_date - timedelta(days=lookback_days)
    historical_start = current_date - timedelta(days=historical_days)
    
    # Filter data for analysis window (last 120 days from current_date)
    recent_data = [d for d in nav_data[:current_index+1] 
                   if d['date'] >= analysis_start]
    
    # Filter data for historical window (last 730 days from current_date)
    historical_data = [d for d in nav_data[:current_index+1] 
                       if d['date'] >= historical_start]
    
    if len(recent_data) < 30 or len(historical_data) < 100:
        return {'error': 'Insufficient data'}
    
    # Calculate Factor 1: Dip Depth
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
    
    # Calculate Factor 2: Historical Context
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
    
    # Calculate Factor 3: Mean Reversion
    mean_nav = sum(d['nav'] for d in recent_data) / len(recent_data)
    if current_nav < mean_nav:
        deviation = ((mean_nav - current_nav) / mean_nav) * 100
        mean_score = min(deviation * 2, 15)
    else:
        mean_score = 0
    
    # Calculate Factor 4: Volatility
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
    
    # Simplified Factor 5: Recovery (use fixed score for backtesting speed)
    recovery_score = 10  # Neutral score
    
    # Factor 6: Fund Type (assume Small Cap = 10 for testing)
    type_score = 10
    
    total_score = dip_score + historical_score + mean_score + volatility_score + recovery_score + type_score
    
    return {
        'date': current_date,
        'nav': current_nav,
        'score': total_score,
        'dip_percentage': dip_percentage,
        'peak_nav': peak_nav,
        'mean_nav': mean_nav,
        'volatility': volatility,
        'recommendation': get_recommendation(total_score)
    }


def get_recommendation(score: float) -> str:
    """Convert score to recommendation"""
    if score >= 75:
        return 'STRONG_BUY'
    elif score >= 60:
        return 'BUY'
    elif score >= 45:
        return 'MODERATE_BUY'
    elif score >= 30:
        return 'WEAK_BUY'
    else:
        return 'HOLD'


def backtest_strategy(
    fund_name: str,
    code: str,
    backtest_period_days: int = 365,
    initial_capital: float = 100000,
    buy_amount: float = 10000
) -> Dict:
    """
    Backtest the dip-buying strategy
    
    Strategy:
    - Evaluate algorithm score every 7 days
    - If score >= 60 (BUY or better), invest based on allocation
    - Track total returns vs buy-and-hold baseline
    """
    
    print(f"\n{'='*80}")
    print(f"🔬 BACKTESTING: {fund_name}")
    print(f"{'='*80}")
    
    # Fetch historical data (3 years to have enough lookback)
    try:
        nav_data = fetch_full_historical_data(code, days=1095)
    except Exception as e:
        return {'error': f'Failed to fetch data: {str(e)}'}
    
    if len(nav_data) < 365:
        return {'error': 'Insufficient data for backtesting'}
    
    # Define backtest period (last X days)
    backtest_start_date = datetime.now() - timedelta(days=backtest_period_days)
    backtest_data_indices = [i for i, d in enumerate(nav_data) 
                              if d['date'] >= backtest_start_date]
    
    if len(backtest_data_indices) < 50:
        return {'error': 'Insufficient backtest period'}
    
    # Strategy tracking
    strategy_capital = initial_capital
    strategy_units = 0
    strategy_transactions = []
    
    # Baseline tracking (buy-and-hold at start)
    baseline_nav_start = nav_data[backtest_data_indices[0]]['nav']
    baseline_units = initial_capital / baseline_nav_start
    
    # Run backtest - evaluate every 7 days
    for i in range(0, len(backtest_data_indices), 7):
        index = backtest_data_indices[i]
        
        # Skip if not enough historical data
        if index < 730:
            continue
        
        # Run algorithm at this point in time
        result = simulate_algorithm_at_point_in_time(nav_data, index)
        
        if result.get('error'):
            continue
        
        score = result['score']
        recommendation = result['recommendation']
        nav = result['nav']
        date = result['date']
        
        # Decision: Buy if score >= 60
        if score >= 60 and strategy_capital >= buy_amount:
            # Calculate allocation based on score
            if score >= 75:
                allocation = 0.40
            elif score >= 60:
                allocation = 0.30
            else:
                allocation = 0.20
            
            invest_amount = min(buy_amount * allocation / 0.30, strategy_capital)
            units_bought = invest_amount / nav
            
            strategy_units += units_bought
            strategy_capital -= invest_amount
            
            strategy_transactions.append({
                'date': date.strftime('%d-%m-%Y'),
                'action': 'BUY',
                'score': score,
                'nav': nav,
                'amount': invest_amount,
                'units': units_bought,
                'dip_percentage': result['dip_percentage']
            })
    
    # Calculate final values
    final_nav = nav_data[-1]['nav']
    final_date = nav_data[-1]['date']
    
    # Strategy final value
    strategy_final_value = (strategy_units * final_nav) + strategy_capital
    strategy_return_pct = ((strategy_final_value - initial_capital) / initial_capital) * 100
    
    # Baseline final value
    baseline_final_value = baseline_units * final_nav
    baseline_return_pct = ((baseline_final_value - initial_capital) / initial_capital) * 100
    
    # Calculate metrics
    num_transactions = len(strategy_transactions)
    total_invested = sum(t['amount'] for t in strategy_transactions)
    avg_buy_nav = total_invested / strategy_units if strategy_units > 0 else 0
    
    return {
        'fund_name': fund_name,
        'fund_code': code,
        'backtest_period_days': backtest_period_days,
        'backtest_start': nav_data[backtest_data_indices[0]]['date'].strftime('%d-%m-%Y'),
        'backtest_end': final_date.strftime('%d-%m-%Y'),
        'initial_capital': initial_capital,
        
        # Strategy Results
        'strategy_transactions': num_transactions,
        'strategy_total_invested': total_invested,
        'strategy_units': strategy_units,
        'strategy_avg_buy_nav': avg_buy_nav,
        'strategy_final_value': strategy_final_value,
        'strategy_return_pct': strategy_return_pct,
        'strategy_capital_remaining': strategy_capital,
        
        # Baseline Results
        'baseline_buy_nav': baseline_nav_start,
        'baseline_units': baseline_units,
        'baseline_final_value': baseline_final_value,
        'baseline_return_pct': baseline_return_pct,
        
        # Comparison
        'outperformance': strategy_return_pct - baseline_return_pct,
        'final_nav': final_nav,
        
        # Transaction details
        'transactions': strategy_transactions,
        
        'error': None
    }


def print_backtest_results(result: Dict) -> None:
    """Pretty print backtest results"""
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"\n📅 Backtest Period: {result['backtest_start']} to {result['backtest_end']}")
    print(f"💰 Initial Capital: ₹{result['initial_capital']:,.0f}")
    print(f"🎯 Strategy: Buy when score >= 60\n")
    
    print("="*80)
    print("📊 STRATEGY PERFORMANCE (Dip-Buying Algorithm)")
    print("="*80)
    print(f"Number of Purchases:     {result['strategy_transactions']}")
    print(f"Total Amount Invested:   ₹{result['strategy_total_invested']:,.2f}")
    print(f"Units Accumulated:       {result['strategy_units']:.4f}")
    print(f"Average Buy NAV:         ₹{result['strategy_avg_buy_nav']:.2f}")
    print(f"Capital Remaining:       ₹{result['strategy_capital_remaining']:,.2f}")
    print(f"Final Portfolio Value:   ₹{result['strategy_final_value']:,.2f}")
    
    strategy_return = result['strategy_return_pct']
    if strategy_return >= 0:
        print(f"✅ Total Return:          +{strategy_return:.2f}%")
    else:
        print(f"❌ Total Return:          {strategy_return:.2f}%")
    
    print("\n" + "="*80)
    print("📈 BASELINE PERFORMANCE (Buy & Hold)")
    print("="*80)
    print(f"Buy NAV (Day 1):         ₹{result['baseline_buy_nav']:.2f}")
    print(f"Units Purchased:         {result['baseline_units']:.4f}")
    print(f"Final Portfolio Value:   ₹{result['baseline_final_value']:,.2f}")
    
    baseline_return = result['baseline_return_pct']
    if baseline_return >= 0:
        print(f"✅ Total Return:          +{baseline_return:.2f}%")
    else:
        print(f"❌ Total Return:          {baseline_return:.2f}%")
    
    print("\n" + "="*80)
    print("🏆 COMPARISON")
    print("="*80)
    
    outperformance = result['outperformance']
    if outperformance > 0:
        print(f"✅ Algorithm OUTPERFORMED by: +{outperformance:.2f}%")
        print(f"   Strategy is BETTER than buy-and-hold!")
    elif outperformance == 0:
        print(f"➖ Algorithm matched buy-and-hold (0.00%)")
    else:
        print(f"❌ Algorithm UNDERPERFORMED by: {outperformance:.2f}%")
        print(f"   Buy-and-hold was BETTER")
    
    print(f"\nFinal NAV: ₹{result['final_nav']:.2f}")
    
    # Show transactions
    if result['transactions']:
        print("\n" + "="*80)
        print(f"📝 TRANSACTION HISTORY ({len(result['transactions'])} purchases)")
        print("="*80)
        print(f"{'Date':<12} {'Score':<6} {'Dip%':<7} {'NAV':<10} {'Amount':<12} {'Units':<10}")
        print("-"*80)
        
        for t in result['transactions']:
            print(f"{t['date']:<12} {t['score']:<6.1f} {t['dip_percentage']:<7.2f} "
                  f"₹{t['nav']:<9.2f} ₹{t['amount']:<11,.0f} {t['units']:<10.4f}")
    
    print("="*80)


def backtest_all_funds(backtest_days: int = 365):
    """Run backtest on all funds"""
    funds = get_mf_funds()
    results = []
    
    print("\n" + "🔬 " + "="*78)
    print("BACKTESTING ALL FUNDS - Dip Buying Strategy")
    print("="*80)
    print(f"Backtest Period: Last {backtest_days} days")
    print(f"Initial Capital: ₹1,00,000 per fund")
    print(f"Strategy: Buy ₹10,000 when algorithm score >= 60")
    print("="*80)
    
    for fund in funds:
        if not fund.get('code'):
            continue
        
        try:
            result = backtest_strategy(
                fund_name=fund['fund_name'],
                code=fund['code'],
                backtest_period_days=backtest_days,
                initial_capital=100000,
                buy_amount=10000
            )
            
            if not result.get('error'):
                results.append(result)
                print_backtest_results(result)
        except Exception as e:
            print(f"\n❌ Error backtesting {fund['fund_name']}: {str(e)}")
    
    # Summary
    if results:
        print("\n\n" + "="*80)
        print("📊 BACKTEST SUMMARY - ALL FUNDS")
        print("="*80)
        
        winning_strategies = [r for r in results if r['outperformance'] > 0]
        losing_strategies = [r for r in results if r['outperformance'] <= 0]
        
        print(f"\n✅ Funds where algorithm OUTPERFORMED: {len(winning_strategies)}")
        for r in sorted(winning_strategies, key=lambda x: x['outperformance'], reverse=True):
            print(f"   {r['fund_name']:<50} +{r['outperformance']:.2f}%")
        
        print(f"\n❌ Funds where algorithm UNDERPERFORMED: {len(losing_strategies)}")
        for r in sorted(losing_strategies, key=lambda x: x['outperformance']):
            print(f"   {r['fund_name']:<50} {r['outperformance']:.2f}%")
        
        avg_outperformance = sum(r['outperformance'] for r in results) / len(results)
        win_rate = (len(winning_strategies) / len(results)) * 100
        
        print(f"\n{'='*80}")
        print(f"Win Rate: {win_rate:.1f}% ({len(winning_strategies)}/{len(results)} funds)")
        print(f"Average Outperformance: {avg_outperformance:+.2f}%")
        
        if avg_outperformance > 0:
            print(f"\n🎉 CONCLUSION: Algorithm is EFFECTIVE on average!")
        else:
            print(f"\n⚠️  CONCLUSION: Algorithm needs refinement")
        
        print("="*80)
    
    return results


if __name__ == "__main__":
    # Run backtest on all funds for the last 1 year
    results = backtest_all_funds(backtest_days=365)

