"""
Screener.in Data Fetcher
More reliable fundamental data for Indian stocks
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import time
import re


# Known symbol mappings (NSE -> Screener.in)
SYMBOL_MAPPINGS = {
    'HDFCBANK': 'HDFC-BANK',
    'ASIANPAINT': 'ASIANPAINTS',
    'BAJFINANCE': 'BAJAJ-FINSERV',  # Sometimes needs adjustment
    'BHARTIARTL': 'BHARTIARTL',
    # Add more as we discover them
}


def get_screener_symbol_variations(nse_symbol: str) -> List[str]:
    """
    Get possible Screener.in symbol variations for an NSE symbol
    
    Args:
        nse_symbol: NSE stock symbol
    
    Returns:
        List of possible symbol variations to try
    """
    variations = []
    
    # 1. Check if we have a known mapping
    if nse_symbol in SYMBOL_MAPPINGS:
        variations.append(SYMBOL_MAPPINGS[nse_symbol])
    
    # 2. Try exact symbol
    variations.append(nse_symbol)
    
    # 3. Try with 'S' at end (common variation)
    if not nse_symbol.endswith('S'):
        variations.append(nse_symbol + 'S')
    
    # 4. Try without last character if it ends with certain letters
    if len(nse_symbol) > 4 and nse_symbol[-1] in ['T', 'L', 'D']:
        variations.append(nse_symbol[:-1])
    
    # 5. Try with hyphen before common suffixes
    for suffix in ['BANK', 'FIN', 'FINANCE', 'IND', 'LTD']:
        if nse_symbol.endswith(suffix) and len(nse_symbol) > len(suffix):
            base = nse_symbol[:-len(suffix)]
            variations.append(f"{base}-{suffix}")
    
    return variations


def search_screener_symbol(query: str) -> Optional[str]:
    """
    Search Screener.in for a stock symbol
    
    Args:
        query: Search query (symbol or company name)
    
    Returns:
        Screener.in symbol if found, None otherwise
    """
    try:
        # Screener.in search API
        search_url = f"https://www.screener.in/api/company/search/?q={query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        response = requests.get(search_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            results = response.json()
            
            # Return first result's URL slug
            if results and len(results) > 0:
                first_result = results[0]
                if 'url' in first_result:
                    # Extract symbol from URL like '/company/TCS/' or '/company/TCS/consolidated/'
                    url = first_result['url']
                    parts = url.strip('/').split('/')
                    
                    # Symbol is the part after 'company'
                    if 'company' in parts:
                        company_index = parts.index('company')
                        if company_index + 1 < len(parts):
                            symbol = parts[company_index + 1]
                            return symbol
        
        return None
    
    except Exception as e:
        print(f"    Search failed: {e}")
        return None


def fetch_fundamentals_from_screener(symbol: str, try_search: bool = True) -> Optional[Dict]:
    """
    Fetch fundamental data from Screener.in with automatic symbol variation handling
    
    This is more reliable than yfinance for Indian stocks
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
        try_search: If True, will search Screener.in if direct lookup fails
    
    Returns:
        Dictionary with fundamental metrics or None
    """
    # Get all possible symbol variations
    symbol_variations = get_screener_symbol_variations(symbol)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    # Try each variation
    for variation in symbol_variations:
        try:
            url = f"https://www.screener.in/company/{variation}/"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            # If successful, parse the data
            if response.status_code == 200:
                if variation != symbol:
                    print(f"    ℹ️  Using Screener symbol '{variation}' for '{symbol}'")
                
                return _parse_screener_page(response.content, variation)
            
        except requests.RequestException:
            # Try next variation
            continue
    
    # If all variations failed and search is enabled, try searching
    if try_search:
        print(f"    🔍 Searching Screener.in for '{symbol}'...")
        searched_symbol = search_screener_symbol(symbol)
        
        if searched_symbol and searched_symbol not in symbol_variations:
            print(f"    ✓ Found: '{searched_symbol}'")
            try:
                url = f"https://www.screener.in/company/{searched_symbol}/"
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Update mapping for future use
                    SYMBOL_MAPPINGS[symbol] = searched_symbol
                    return _parse_screener_page(response.content, searched_symbol)
            
            except requests.RequestException:
                pass
    
    print(f"  ⚠️  Could not find '{symbol}' on Screener.in (tried {len(symbol_variations)} variations)")
    return None


def _parse_screener_page(html_content, symbol: str) -> Optional[Dict]:
    """
    Parse Screener.in page HTML to extract fundamentals
    
    Args:
        html_content: HTML content from Screener.in
        symbol: Symbol being parsed (for error messages)
    
    Returns:
        Dictionary with fundamental metrics or None
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        fundamentals = {}
        
        # Extract from ratios section
        ratios_section = soup.find('ul', {'id': 'top-ratios'})
        
        if ratios_section:
            ratio_items = ratios_section.find_all('li', {'class': 'flex flex-space-between'})
            
            for item in ratio_items:
                name_elem = item.find('span', {'class': 'name'})
                value_elem = item.find('span', {'class': 'number'})
                
                if name_elem and value_elem:
                    name = name_elem.text.strip()
                    value_text = value_elem.text.strip()
                    
                    # Parse different metrics
                    try:
                        if 'Market Cap' in name:
                            # Extract number from "₹1,23,456 Cr"
                            value_clean = re.sub(r'[^\d.]', '', value_text)
                            fundamentals['market_cap'] = float(value_clean) * 10000000 if value_clean else 0
                        
                        elif 'Current Price' in name:
                            value_clean = re.sub(r'[^\d.]', '', value_text)
                            fundamentals['current_price'] = float(value_clean) if value_clean else 0
                        
                        elif 'Stock P/E' in name:
                            value_clean = re.sub(r'[^\d.]', '', value_text)
                            fundamentals['pe_ratio'] = float(value_clean) if value_clean else 0
                        
                        elif 'Book Value' in name:
                            value_clean = re.sub(r'[^\d.]', '', value_text)
                            fundamentals['book_value'] = float(value_clean) if value_clean else 0
                        
                        elif 'Dividend Yield' in name:
                            value_clean = re.sub(r'[^\d.]', '', value_text)
                            fundamentals['dividend_yield'] = float(value_clean) if value_clean else 0
                        
                        elif 'ROCE' in name:
                            value_clean = re.sub(r'[^\d.-]', '', value_text)
                            fundamentals['roce'] = float(value_clean) if value_clean else 0
                        
                        elif 'ROE' in name:
                            value_clean = re.sub(r'[^\d.-]', '', value_text)
                            fundamentals['roe'] = float(value_clean) if value_clean else 0
                        
                        elif 'Debt to Equity' in name or 'Debt/Equity' in name:
                            value_clean = re.sub(r'[^\d.]', '', value_text)
                            fundamentals['debt_to_equity'] = float(value_clean) if value_clean else 0
                    
                    except (ValueError, AttributeError):
                        continue
        
        # Extract from quarters/year table for growth metrics
        quarters_table = soup.find('section', {'id': 'quarters'})
        
        if quarters_table:
            # Try to get sales growth and profit growth from the table
            try:
                rows = quarters_table.find_all('tr')
                
                for row in rows:
                    header = row.find('td')
                    if header:
                        header_text = header.text.strip()
                        
                        if 'Sales Growth' in header_text or 'Revenue Growth' in header_text:
                            # Get latest quarter value
                            cells = row.find_all('td')
                            if len(cells) > 1:
                                value_text = cells[-1].text.strip()
                                value_clean = re.sub(r'[^\d.-]', '', value_text)
                                fundamentals['revenue_growth'] = float(value_clean) if value_clean else 0
                        
                        elif 'Profit Growth' in header_text or 'Net Profit Growth' in header_text:
                            cells = row.find_all('td')
                            if len(cells) > 1:
                                value_text = cells[-1].text.strip()
                                value_clean = re.sub(r'[^\d.-]', '', value_text)
                                fundamentals['profit_growth'] = float(value_clean) if value_clean else 0
                        
                        elif 'OPM' in header_text or 'Operating Profit Margin' in header_text:
                            cells = row.find_all('td')
                            if len(cells) > 1:
                                value_text = cells[-1].text.strip()
                                value_clean = re.sub(r'[^\d.-]', '', value_text)
                                fundamentals['operating_margin'] = float(value_clean) if value_clean else 0
                        
                        elif 'Net Profit Margin' in header_text or 'NPM' in header_text:
                            cells = row.find_all('td')
                            if len(cells) > 1:
                                value_text = cells[-1].text.strip()
                                value_clean = re.sub(r'[^\d.-]', '', value_text)
                                fundamentals['profit_margin'] = float(value_clean) if value_clean else 0
            
            except Exception as e:
                print(f"  Warning: Could not parse growth metrics: {e}")
        
        # Calculate P/B ratio if we have price and book value
        if 'current_price' in fundamentals and 'book_value' in fundamentals:
            if fundamentals['book_value'] > 0:
                fundamentals['pb_ratio'] = fundamentals['current_price'] / fundamentals['book_value']
        
        # Add 52-week high/low from another section if available
        price_section = soup.find('div', {'class': 'price-volume'})
        if price_section:
            try:
                high_low_text = price_section.text
                high_match = re.search(r'52w High[:\s]+₹?([\d,]+\.?\d*)', high_low_text)
                low_match = re.search(r'52w Low[:\s]+₹?([\d,]+\.?\d*)', high_low_text)
                
                if high_match:
                    fundamentals['fifty_two_week_high'] = float(high_match.group(1).replace(',', ''))
                if low_match:
                    fundamentals['fifty_two_week_low'] = float(low_match.group(1).replace(',', ''))
            except:
                pass
        
        return fundamentals if fundamentals else None
    
    except Exception as e:
        print(f"  ⚠️  Error parsing Screener.in data for {symbol}: {str(e)}")
        return None


def fetch_fundamentals_hybrid(symbol: str, exchange: str = 'NSE') -> Dict:
    """
    Hybrid approach: Try Screener.in first, fallback to yfinance
    
    Args:
        symbol: Stock symbol
        exchange: Exchange (NSE or BSE)
    
    Returns:
        Dictionary with fundamental metrics
    """
    print(f"  📊 Fetching fundamentals for {symbol}...")
    
    # Try Screener.in first
    print(f"     Trying Screener.in...")
    screener_data = fetch_fundamentals_from_screener(symbol)
    
    if screener_data and len(screener_data) >= 5:  # Got reasonable data
        print(f"     ✅ Got data from Screener.in ({len(screener_data)} metrics)")
        return screener_data
    
    # Fallback to yfinance
    print(f"     ⚠️  Screener.in incomplete, falling back to yfinance...")
    from stock_data_fetcher import fetch_fundamentals
    yfinance_data = fetch_fundamentals(symbol, exchange)
    
    # Merge if we got partial data from both
    if screener_data and yfinance_data:
        # Prefer Screener.in data for key metrics
        merged = yfinance_data.copy()
        for key in ['roe', 'pe_ratio', 'debt_to_equity', 'profit_growth', 'revenue_growth', 'profit_margin']:
            if key in screener_data and screener_data[key] != 0:
                merged[key] = screener_data[key]
        return merged
    
    return yfinance_data if yfinance_data else {}


if __name__ == "__main__":
    # Test with a few stocks
    print("🧪 Testing Screener.in Data Fetcher\n")
    print("="*80)
    
    test_stocks = ['RELIANCE', 'TCS', 'ASIANPAINT', 'INFY']
    
    for symbol in test_stocks:
        print(f"\n📊 {symbol}")
        print("-"*80)
        
        data = fetch_fundamentals_from_screener(symbol)
        
        if data:
            print(f"✅ Retrieved {len(data)} metrics:")
            for key, value in sorted(data.items()):
                if isinstance(value, float):
                    print(f"  • {key:20s}: {value:.2f}")
                else:
                    print(f"  • {key:20s}: {value}")
        else:
            print("❌ Failed to retrieve data")
        
        # Be respectful - rate limit
        time.sleep(2)
    
    print("\n" + "="*80)
    print("\n💡 Comparison Test: Asian Paints")
    print("="*80)
    
    print("\n1️⃣  Screener.in:")
    screener_data = fetch_fundamentals_from_screener('ASIANPAINT')
    if screener_data:
        print(f"   ROE: {screener_data.get('roe', 0):.2f}%")
        print(f"   P/E: {screener_data.get('pe_ratio', 0):.2f}")
        print(f"   Profit Growth: {screener_data.get('profit_growth', 0):.2f}%")
        print(f"   Profit Margin: {screener_data.get('profit_margin', 0):.2f}%")
    
    time.sleep(2)
    
    print("\n2️⃣  yfinance (for comparison):")
    from stock_data_fetcher import fetch_fundamentals
    yf_data = fetch_fundamentals('ASIANPAINT', 'NSE')
    print(f"   ROE: {yf_data.get('roe', 0):.2f}%")
    print(f"   P/E: {yf_data.get('pe_ratio', 0):.2f}")
    print(f"   Profit Growth: {yf_data.get('profit_growth', 0):.2f}%")
    print(f"   Profit Margin: {yf_data.get('profit_margin', 0):.2f}%")

