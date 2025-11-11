"""
Stock Data Fetcher
Fetches price and fundamental data for Indian stocks
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics


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
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
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
        
        # Extract key fundamentals
        fundamentals = {
            'pe_ratio': info.get('trailingPE', 0) or info.get('forwardPE', 0) or 0,
            'pb_ratio': info.get('priceToBook', 0) or 0,
            'debt_to_equity': info.get('debtToEquity', 0) or 0,
            'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
            'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0,
            'profit_growth': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0,  # ⭐ NEW
            'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
            'market_cap': info.get('marketCap', 0),
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'current_price': info.get('currentPrice', 0) or info.get('regularMarketPrice', 0) or 0,
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0) or 0,
            'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0) or 0,
        }
        
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
        print(f"   ✅ P/E Ratio: {fundamentals['pe_ratio']:.2f}")
        print(f"   ✅ ROE: {fundamentals['roe']:.2f}%")
        print(f"   ✅ Debt/Equity: {fundamentals['debt_to_equity']:.2f}")
    
    if price_data:
        print(f"\n3. Calculating technical indicators...")
        rsi = calculate_rsi(price_data)
        print(f"   RSI: {rsi:.2f}")
        
        support = calculate_support_level(price_data)
        print(f"   Support Level: ₹{support['support_level']:.2f}")
        print(f"   Near Support: {support['near_support']}")
        
        volume_ratio = calculate_volume_ratio(price_data)
        print(f"   Volume Ratio: {volume_ratio:.2f}x average")

