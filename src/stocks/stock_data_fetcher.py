"""
Stock Data Fetcher
Fetches price and fundamental data for Indian stocks
"""

from datetime import datetime, timedelta
from typing import Dict, List
import statistics

from config import FUNDAMENTAL_DEFAULTS, DATA_QUALITY, API_SETTINGS


def fetch_stock_data(symbol: str, days: int = 730, exchange: str = 'NSE') -> List[Dict]:
    """
    Fetch stock price data using yfinance
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE')
        days: Number of days of historical data
        exchange: 'NSE' or 'BSE'
    
    Returns:
        List of dictionaries with date, close, volume, high, low
    """
    try:
        import yfinance as yf
    except ImportError:
        print("❌ yfinance not installed. Run: pip install yfinance")
        return []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Add exchange suffix
    suffix = '.NS' if exchange == 'NSE' else '.BO'
    ticker = f"{symbol}{suffix}"
    
    try:
        print(f"  Fetching data for {ticker}...")
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        
        if data.empty:
            print(f"  ⚠️  No data available for {ticker}")
            return []
        
        price_data = []
        for date, row in data.iterrows():
            price_data.append({
                'date': date.to_pydatetime(),
                'close': float(row['Close'].iloc[0]) if hasattr(row['Close'], 'iloc') else float(row['Close']),
                'volume': int(row['Volume'].iloc[0]) if hasattr(row['Volume'], 'iloc') and 'Volume' in row else (int(row['Volume']) if 'Volume' in row else 0),
                'high': float(row['High'].iloc[0]) if hasattr(row['High'], 'iloc') else float(row['High']),
                'low': float(row['Low'].iloc[0]) if hasattr(row['Low'], 'iloc') else float(row['Low']),
                'open': float(row['Open'].iloc[0]) if hasattr(row['Open'], 'iloc') else float(row['Open'])
            })
        
        return price_data
    
    except Exception as e:
        print(f"  ❌ Error fetching {ticker}: {str(e)}")
        return []


def fetch_fundamentals(symbol: str, exchange: str = 'NSE') -> Dict:
    """
    Fetch fundamental data for a stock
    
    Returns:
        Dictionary with P/E, ROE, Debt-to-Equity, etc.
    """
    try:
        import yfinance as yf
    except ImportError:
        return {}
    
    suffix = '.NS' if exchange == 'NSE' else '.BO'
    ticker = f"{symbol}{suffix}"
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Helper function to safely extract values with fallback
        def safe_get_ratio(info_dict, primary_key, secondary_key=None, multiply_by_100=False):
            """Safely extract values with fallback"""
            value = info_dict.get(primary_key)
            if value is None and secondary_key:
                value = info_dict.get(secondary_key)
            if value is None or value == 0:
                return 0
            return (value * 100) if multiply_by_100 else value
        
        # Extract key fundamentals with better handling
        fundamentals = {
            'pe_ratio': safe_get_ratio(info, 'trailingPE', 'forwardPE'),
            'pb_ratio': safe_get_ratio(info, 'priceToBook'),
            'debt_to_equity': safe_get_ratio(info, 'debtToEquity'),
            'roe': safe_get_ratio(info, 'returnOnEquity', multiply_by_100=True),
            'revenue_growth': safe_get_ratio(info, 'revenueGrowth', multiply_by_100=True),
            'profit_growth': safe_get_ratio(info, 'earningsGrowth', 'earningsQuarterlyGrowth', multiply_by_100=True),
            'profit_margin': safe_get_ratio(info, 'profitMargins', 'netIncomeToCommon', multiply_by_100=True),
            'market_cap': safe_get_ratio(info, 'marketCap'),
            'dividend_yield': min(safe_get_ratio(info, 'dividendYield', multiply_by_100=True), 20),  # Cap at 20% (sanity check)
            'current_price': safe_get_ratio(info, 'currentPrice', 'regularMarketPrice'),
            'fifty_two_week_high': safe_get_ratio(info, 'fiftyTwoWeekHigh'),
            'fifty_two_week_low': safe_get_ratio(info, 'fiftyTwoWeekLow'),
            'peg_ratio': safe_get_ratio(info, 'pegRatio'),
            'promoter_holding': safe_get_ratio(info, 'heldPercentInsiders', multiply_by_100=True),
            'pledged_shares': 0,  # Placeholder: yfinance doesn't provide pledging data for Indian stocks
            'median_pe': 0,       # Placeholder: Requires historical earnings data
        }
        
        # Try to calculate ROE manually if it's 0
        if fundamentals['roe'] == 0:
            # Try alternate calculation: ROE from trailing EPS and book value
            trailing_eps = info.get('trailingEps', 0)
            book_value = info.get('bookValue', 0)
            if trailing_eps and book_value and book_value > 0:
                calculated_roe = (trailing_eps / book_value) * 100
                if 0 < calculated_roe < 100:  # Sanity check
                    fundamentals['roe'] = calculated_roe
        
        # Apply defaults for missing critical metrics (from config)
        if DATA_QUALITY['use_defaults_for_missing']:
            estimated_fields = []
            for key, default_value in FUNDAMENTAL_DEFAULTS.items():
                if key in fundamentals and fundamentals[key] == 0:
                    fundamentals[key] = default_value
                    estimated_fields.append(key)
            
            # Mark the data quality
            fundamentals['_data_quality'] = 'estimated' if estimated_fields else 'actual'
            fundamentals['_estimated_fields'] = estimated_fields
            
            # Warn about estimated values
            if estimated_fields and DATA_QUALITY['warn_on_estimated']:
                print(f"  ℹ️  Using defaults for {ticker}: {', '.join(estimated_fields)}")
        else:
            fundamentals['_data_quality'] = 'actual'
            fundamentals['_estimated_fields'] = []
        
        return fundamentals
    
    except Exception as e:
        print(f"  ⚠️  Could not fetch fundamentals for {ticker}: {str(e)}")
        return {}


def calculate_rsi(price_data: List[Dict], period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        price_data: List of price dictionaries
        period: RSI period (default 14)
    
    Returns:
        RSI value (0-100)
    """
    if len(price_data) < period + 1:
        return 50  # Neutral if not enough data
    
    closes = [d['close'] for d in price_data]
    
    gains = []
    losses = []
    
    for i in range(1, len(closes)):
        change = closes[i] - closes[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    if len(gains) < period:
        return 50
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_support_level(price_data: List[Dict], window: int = 30) -> Dict:
    """
    Calculate if current price is near support level
    
    Args:
        price_data: List of price dictionaries
        window: Lookback window
    
    Returns:
        Dictionary with support info
    """
    if len(price_data) < window:
        return {'near_support': False, 'support_level': 0}
    
    recent_data = price_data[-window:]
    current_price = price_data[-1]['close']
    
    # Find local minimums (support levels)
    lows = [d['low'] for d in recent_data]
    support_level = min(lows)
    
    # Check if current price is within 2% of support
    distance_from_support = ((current_price - support_level) / support_level) * 100
    near_support = distance_from_support <= 2.0
    
    return {
        'near_support': near_support,
        'support_level': support_level,
        'distance_pct': distance_from_support
    }


def calculate_volume_ratio(price_data: List[Dict], period: int = 20) -> float:
    """
    Calculate current volume vs average volume
    
    Args:
        price_data: List of price dictionaries
        period: Period for average calculation
    
    Returns:
        Volume ratio (current / average)
    """
    if len(price_data) < period + 1:
        return 1.0
    
    volumes = [d['volume'] for d in price_data[-period-1:]]
    
    if not volumes or volumes[-1] == 0:
        return 1.0
    
    avg_volume = sum(volumes[:-1]) / len(volumes[:-1])
    
    if avg_volume == 0:
        return 1.0
    
    return volumes[-1] / avg_volume


if __name__ == "__main__":
    # Test the data fetcher
    print("🧪 Testing Stock Data Fetcher\n")
    
    test_symbol = "RELIANCE"
    
    print(f"1. Fetching price data for {test_symbol}...")
    price_data = fetch_stock_data(test_symbol, days=90)
    
    if price_data:
        print(f"   ✅ Retrieved {len(price_data)} days of data")
        print(f"   Latest: {price_data[-1]['date'].strftime('%d-%m-%Y')}")
        print(f"   Close: ₹{price_data[-1]['close']:.2f}")
    
    print(f"\n2. Fetching fundamentals for {test_symbol}...")
    fundamentals = fetch_fundamentals(test_symbol)
    
    if fundamentals:
        print(f"   ✅ P/E Ratio: {fundamentals.get('pe_ratio', 0):.2f}")
        print(f"   ✅ P/B Ratio: {fundamentals.get('pb_ratio', 0):.2f}")
        print(f"   ✅ ROE: {fundamentals.get('roe', 0):.2f}%")
        print(f"   ✅ Debt/Equity: {fundamentals.get('debt_to_equity', 0):.2f}")
        print(f"   ✅ Revenue Growth: {fundamentals.get('revenue_growth', 0):.2f}%")
        print(f"   ✅ Profit Growth: {fundamentals.get('profit_growth', 0):.2f}% ⭐")
        print(f"   ✅ Profit Margin: {fundamentals.get('profit_margin', 0):.2f}% ⭐")
        print(f"   💰 Market Cap: ₹{fundamentals.get('market_cap', 0)/10000000:.2f} Cr")
        print(f"   📈 Current Price: ₹{fundamentals.get('current_price', 0):.2f}")
        print(f"   📊 52-Week Range: ₹{fundamentals.get('fifty_two_week_low', 0):.2f} - ₹{fundamentals.get('fifty_two_week_high', 0):.2f}")
    
    if price_data:
        print(f"\n3. Calculating technical indicators...")
        rsi = calculate_rsi(price_data)
        print(f"   RSI: {rsi:.2f}")
        
        support = calculate_support_level(price_data)
        print(f"   Support Level: ₹{support['support_level']:.2f}")
        print(f"   Near Support: {support['near_support']}")
        
        volume_ratio = calculate_volume_ratio(price_data)
        print(f"   Volume Ratio: {volume_ratio:.2f}x average")

