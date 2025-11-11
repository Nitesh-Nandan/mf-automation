"""
Stock Dip Analyzer - Blue-Chip Stock Version
8-factor algorithm for identifying stock dip-buying opportunities
"""

import csv
import statistics
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path

from stock_data_fetcher import (
    fetch_stock_data, fetch_fundamentals,
    calculate_rsi, calculate_support_level, calculate_volume_ratio
)
from fundamental_analyzer import calculate_fundamental_score, is_quality_stock


def load_stocks_watchlist():
    """Load stocks from watchlist CSV"""
    script_dir = Path(__file__).parent
    csv_path = script_dir / "stocks_watchlist.csv"
    
    stocks = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            stocks.append(row)
    
    return stocks


def calculate_volatility(price_data: List[Dict]) -> float:
    """Calculate annualized volatility"""
    if len(price_data) < 2:
        return 0.0
    
    returns = []
    for i in range(1, len(price_data)):
        daily_return = (price_data[i]['close'] - price_data[i-1]['close']) / price_data[i-1]['close']
        returns.append(daily_return)
    
    if not returns:
        return 0.0
    
    volatility = statistics.stdev(returns) * (252 ** 0.5) * 100
    return volatility


def calculate_recovery_speed(price_data: List[Dict]) -> Dict:
    """Analyze historical recovery speed from dips"""
    price_data_sorted = sorted(price_data, key=lambda x: x['date'])
    
    recoveries = []
    in_dip = False
    dip_start_idx = 0
    peak_price = price_data_sorted[0]['close']
    
    for i, entry in enumerate(price_data_sorted):
        current_price = entry['close']
        
        if current_price > peak_price:
            if in_dip and i > dip_start_idx:
                recovery_days = (entry['date'] - price_data_sorted[dip_start_idx]['date']).days
                recoveries.append(recovery_days)
                in_dip = False
            peak_price = current_price
        
        dip_pct = ((peak_price - current_price) / peak_price) * 100
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


def analyze_stock_dip(
    symbol: str,
    name: str,
    sector: str,
    market_cap: str,
    exchange: str = 'NSE',
    analysis_days: int = 120,
    historical_days: int = 730,
    mode: str = 'conservative'
) -> Dict:
    """
    Comprehensive 8-factor stock dip analysis
    
    Factors:
    1. Dip Depth (0-25 pts)
    2. Historical Context (0-20 pts)
    3. Mean Reversion (0-15 pts)
    4. Volatility (0-15 pts)
    5. Recovery Speed (0-15 pts)
    6. Market Cap (0-5 pts)
    7. Fundamentals (0-15 pts) ← Stock-specific
    8. Technicals (0-10 pts) ← Stock-specific
    
    Total: 0-120 pts (normalized to 100)
    """
    
    try:
        # Fetch price data
        price_data = fetch_stock_data(symbol, days=historical_days, exchange=exchange)
        
        if not price_data or len(price_data) < 100:
            return {'error': f'Insufficient price data for {symbol}'}
        
        # Fetch fundamentals
        fundamentals = fetch_fundamentals(symbol, exchange=exchange)
        
        if not fundamentals:
            return {'error': f'Could not fetch fundamentals for {symbol}'}
        
        # Check if it's a quality stock
        quality_check = is_quality_stock(fundamentals, min_score=8)
        if not quality_check['is_quality']:
            return {
                'error': f'{symbol} did not pass quality checks',
                'quality_check': quality_check
            }
        
        # Get recent data for current analysis
        recent_data = price_data[-analysis_days:] if len(price_data) >= analysis_days else price_data
        
        score_breakdown = {}
        total_score = 0
        
        # === FACTOR 1: Dip Depth (0-25 points) ===
        current_price = price_data[-1]['close']
        peak_price = max([d['close'] for d in recent_data])
        dip_percentage = ((peak_price - current_price) / peak_price) * 100
        
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
        
        score_breakdown['dip_depth'] = {
            'score': dip_score,
            'value': dip_percentage,
            'max': 25
        }
        total_score += dip_score
        
        # === FACTOR 2: Historical Context (0-20 points) ===
        # Find maximum historical dip
        max_dip = 0
        running_max = price_data[0]['close']
        for entry in price_data:
            if entry['close'] > running_max:
                running_max = entry['close']
            dip = ((running_max - entry['close']) / running_max) * 100
            if dip > max_dip:
                max_dip = dip
        
        if max_dip > 0:
            dip_ratio = (dip_percentage / max_dip) * 100
            
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
        
        score_breakdown['historical_context'] = {
            'score': historical_score,
            'current_vs_max_ratio': round(dip_ratio, 2) if max_dip > 0 else 0,
            'max_historical_dip': round(max_dip, 2),
            'max': 20
        }
        total_score += historical_score
        
        # === FACTOR 3: Mean Reversion (0-15 points) ===
        mean_price = statistics.mean([d['close'] for d in recent_data])
        
        if current_price < mean_price:
            deviation = ((mean_price - current_price) / mean_price) * 100
            mean_score = min(deviation * 2, 15)
        else:
            mean_score = 0
        
        score_breakdown['mean_reversion'] = {
            'score': round(mean_score, 2),
            'below_mean_pct': round(((mean_price - current_price) / mean_price) * 100, 2),
            'mean_price': round(mean_price, 2),
            'max': 15
        }
        total_score += mean_score
        
        # === FACTOR 4: Volatility (0-15 points) ===
        volatility = calculate_volatility(price_data)
        
        # Stocks can be more volatile than MFs
        if 20 <= volatility <= 35:
            volatility_score = 15  # Sweet spot for stocks
        elif 35 < volatility <= 50:
            volatility_score = 12
        elif 15 <= volatility < 20:
            volatility_score = 10
        elif volatility > 50:
            volatility_score = 5  # Too risky
        else:
            volatility_score = 3  # Too stable
        
        score_breakdown['volatility'] = {
            'score': volatility_score,
            'value': round(volatility, 2),
            'max': 15
        }
        total_score += volatility_score
        
        # === FACTOR 5: Recovery Speed (0-15 points) ===
        recovery_stats = calculate_recovery_speed(price_data)
        
        if recovery_stats['has_history']:
            avg_recovery = recovery_stats['avg_recovery_days']
            
            if avg_recovery <= 20:
                recovery_score = 15  # Very fast (stocks can recover quickly)
            elif avg_recovery <= 40:
                recovery_score = 12
            elif avg_recovery <= 60:
                recovery_score = 8
            else:
                recovery_score = 4
        else:
            recovery_score = 8
        
        score_breakdown['recovery_track_record'] = {
            'score': recovery_score,
            'avg_recovery_days': recovery_stats.get('avg_recovery_days', 0),
            'recovery_count': recovery_stats.get('recovery_count', 0),
            'max': 15
        }
        total_score += recovery_score
        
        # === FACTOR 6: Market Cap (0-5 points) ===
        cap_scores = {
            'large': 5,   # Large caps are safer
            'mid': 7,     # Mid caps have good balance
            'small': 9    # Small caps have higher growth
        }
        cap_score = cap_scores.get(market_cap.lower(), 5)
        # Normalize to 5 max
        cap_score = min(cap_score * 5 // 9, 5)
        
        score_breakdown['market_cap'] = {
            'score': cap_score,
            'category': market_cap,
            'max': 5
        }
        total_score += cap_score
        
        # === FACTOR 7: Fundamentals (0-20 points) ⭐ ENHANCED ===
        fundamental_result = calculate_fundamental_score(fundamentals)
        fundamental_score = fundamental_result['total_score']
        
        score_breakdown['fundamentals'] = {
            'score': fundamental_score,
            'breakdown': fundamental_result['breakdown'],
            'max': 20
        }
        total_score += fundamental_score
        
        # === FACTOR 8: Technicals (0-10 points) ===
        technical_score = 0
        
        # RSI (0-5 points)
        rsi = calculate_rsi(price_data)
        if rsi < 30:
            rsi_score = 5  # Oversold
        elif rsi < 40:
            rsi_score = 4
        elif rsi < 50:
            rsi_score = 3
        else:
            rsi_score = 1
        
        technical_score += rsi_score
        
        # Volume (0-3 points)
        volume_ratio = calculate_volume_ratio(price_data)
        if volume_ratio > 2.0:
            volume_score = 3
        elif volume_ratio > 1.5:
            volume_score = 2
        else:
            volume_score = 1
        
        technical_score += volume_score
        
        # Support Level (0-2 points)
        support = calculate_support_level(price_data)
        support_score = 2 if support['near_support'] else 0
        technical_score += support_score
        
        score_breakdown['technicals'] = {
            'score': technical_score,
            'rsi': round(rsi, 2),
            'volume_ratio': round(volume_ratio, 2),
            'near_support': support['near_support'],
            'max': 10
        }
        total_score += technical_score
        
        # Normalize total score to 100 (from 125: 15+15+15+15+15+5+20+10+10+5)
        final_score = (total_score / 125) * 100
        
        # === GENERATE RECOMMENDATION ===
        thresholds = {
            'ultra_conservative': 75,
            'conservative': 65,
            'moderate': 55,
            'aggressive': 45
        }
        
        threshold = thresholds.get(mode, 65)
        
        if final_score >= 80:
            recommendation = 'STRONG BUY'
            allocation = 0.20  # Max 20% for individual stock
            confidence = 'Very High'
        elif final_score >= 70:
            recommendation = 'BUY'
            allocation = 0.15
            confidence = 'High'
        elif final_score >= 60:
            recommendation = 'MODERATE BUY'
            allocation = 0.10
            confidence = 'Medium'
        elif final_score >= 50:
            recommendation = 'WEAK BUY'
            allocation = 0.05
            confidence = 'Low'
        else:
            recommendation = 'HOLD'
            allocation = 0.0
            confidence = 'None'
        
        triggers_buy = final_score >= threshold
        
        return {
            'symbol': symbol,
            'name': name,
            'sector': sector,
            'total_score': round(final_score, 2),
            'recommendation': recommendation,
            'allocation_percentage': allocation,
            'confidence': confidence,
            'mode': mode,
            'threshold': threshold,
            'triggers_buy': triggers_buy,
            'current_price': round(current_price, 2),
            'peak_price': round(peak_price, 2),
            'dip_percentage': round(dip_percentage, 2),
            'score_breakdown': score_breakdown,
            'fundamentals': fundamentals,
            'quality_check': quality_check,
            'error': None
        }
        
    except Exception as e:
        return {
            'symbol': symbol,
            'name': name,
            'error': f'Error analyzing {symbol}: {str(e)}'
        }


def analyze_all_stocks(mode: str = 'conservative') -> List[Dict]:
    """Analyze all stocks in watchlist"""
    stocks = load_stocks_watchlist()
    results = []
    
    print(f"\n🎯 Analyzing Blue-Chip Stocks - {mode.upper()} MODE")
    print("="*80)
    print("Only analyzing quality stocks (pass fundamental filter)\n")
    
    for stock in stocks:
        print(f"Analyzing {stock['name']} ({stock['symbol']})...")
        
        result = analyze_stock_dip(
            symbol=stock['symbol'],
            name=stock['name'],
            sector=stock['sector'],
            market_cap=stock['market_cap'],
            exchange=stock['exchange'],
            mode=mode
        )
        
        if not result.get('error'):
            results.append(result)
            print(f"  ✅ Score: {result['total_score']:.1f} | {result['recommendation']}")
        else:
            print(f"  ⚠️  {result['error']}")
    
    results.sort(key=lambda x: x['total_score'], reverse=True)
    
    return results


def print_stock_summary(results: List[Dict], mode: str):
    """Print summary of stock analysis"""
    print("\n" + "="*80)
    print(f"📊 STOCK ANALYSIS SUMMARY - {mode.upper()} MODE")
    print("="*80)
    
    if not results:
        print("No stocks passed quality filter")
        return
    
    buy_triggered = [r for r in results if r['triggers_buy']]
    
    print(f"\nThreshold: {results[0]['threshold']} points")
    print(f"Stocks analyzed: {len(results)}")
    print(f"Buy signals triggered: {len(buy_triggered)}")
    
    if buy_triggered:
        print(f"\n✅ STOCKS TO BUY:")
        print(f"{'Stock':<40} {'Price':<12} {'Dip%':<8} {'Score':<8} {'Allocate':<10}")
        print("-"*80)
        for r in buy_triggered:
            alloc_pct = f"{r['allocation_percentage']*100:.0f}%"
            print(f"{r['name']:<40} ₹{r['current_price']:<11.2f} {r['dip_percentage']:<7.1f}% "
                  f"{r['total_score']:<7.1f} {alloc_pct:<10}")
        
        total_allocation = sum(r['allocation_percentage'] for r in buy_triggered)
        print(f"\n💰 Total Suggested Allocation: {total_allocation*100:.0f}% of stock dip-buying reserve")
    else:
        print(f"\n❌ No buy signals at this threshold")
        print(f"\n📊 Top scoring opportunities:")
        print(f"{'Stock':<40} {'Price':<12} {'Dip%':<8} {'Score':<8} {'Status':<15}")
        print("-"*80)
        for r in results[:5]:
            print(f"{r['name']:<40} ₹{r['current_price']:<11.2f} {r['dip_percentage']:<7.1f}% "
                  f"{r['total_score']:<7.1f} {r['recommendation']:<15}")
    
    print("="*80)


if __name__ == "__main__":
    """
    Usage: python stock_dip_analyzer.py
    
    Analyzes blue-chip stocks for dip-buying opportunities
    """
    print("🚀 BLUE-CHIP STOCK DIP ANALYZER")
    print("="*80)
    print("8-factor analysis for quality stock opportunities")
    print("="*80)
    
    # Analyze in conservative mode
    results = analyze_all_stocks(mode='conservative')
    print_stock_summary(results, mode='conservative')
    
    print("\n💡 TIPS:")
    print("  • Stocks are analyzed only if they pass quality checks")
    print("  • Position sizes are smaller than MF (10-20% max per stock)")
    print("  • Diversify across 5-7 stocks maximum")
    print("  • Keep individual positions under 20% of stock reserve")
    print("="*80)

