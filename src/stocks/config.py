"""
Stock Analyzer Configuration
Centralized settings for thresholds, defaults, and scoring parameters
"""

# ==============================================================================
# FUNDAMENTAL DATA DEFAULTS
# ==============================================================================
# Based on Indian market averages (November 2024 research)
# Used when yfinance returns 0 or missing data

FUNDAMENTAL_DEFAULTS = {
    'roe': 15.6,              # Average Return on Equity (%)
    'pe_ratio': 22.5,         # Average Price-to-Earnings ratio
    'profit_margin': 10.0,    # Average net profit margin (%)
    'profit_growth': 9.7,     # Average quarterly profit growth (%)
    'revenue_growth': 9.9,    # Average quarterly revenue growth (%)
    'debt_to_equity': 50.0,   # Average debt/equity ratio (0.5 = 50%)
}


# ==============================================================================
# P/E RATIO SCORING THRESHOLDS
# ==============================================================================
# Adjusted for current Indian market conditions (avg P/E ~22.5)

PE_THRESHOLDS = {
    'undervalued': 18,      # < 18 → 4 points (below market avg)
    'fair': 28,             # 18-28 → 3 points (around market avg)
    'acceptable': 40,       # 28-40 → 2 points (elevated but common)
    'expensive': 60,        # 40-60 → 1 point (high valuation)
    # > 60 → 0 points (overvalued)
}


# ==============================================================================
# QUALITY CHECK THRESHOLDS
# ==============================================================================

QUALITY_THRESHOLDS = {
    'max_pe_ratio': 60,           # Maximum acceptable P/E
    'min_roe': 12.0,              # Minimum ROE (%)
    'max_debt_equity': 100,       # Maximum Debt/Equity ratio
    'min_profit_growth': 0.0,     # Minimum profit growth (%)
    'min_profit_margin': 5.0,     # Minimum profit margin (%)
    'min_fundamental_score': 10,  # Minimum score out of 20
}


# ==============================================================================
# DIP BUYING THRESHOLDS BY MODE
# ==============================================================================

DIP_THRESHOLDS = {
    'ultra_conservative': 75,
    'conservative': 65,
    'moderate': 55,
    'aggressive': 45,
}


# ==============================================================================
# POSITION SIZING LIMITS
# ==============================================================================

POSITION_LIMITS = {
    'max_per_stock': 0.20,        # Max 20% of portfolio in one stock
    'max_total_stocks': 7,        # Max 7 different stocks
    'min_investment': 5000,       # Minimum investment per stock (₹)
}


# ==============================================================================
# DATA QUALITY SETTINGS
# ==============================================================================

DATA_QUALITY = {
    'use_defaults_for_missing': True,     # Use defaults when data missing
    'warn_on_estimated': True,            # Warn when using estimated values
    'adjust_score_for_estimates': True,   # Lower threshold if many estimates
    'max_estimated_fields': 3,            # Max fields before score adjustment
}


# ==============================================================================
# MARKET CAP CATEGORIZATION
# ==============================================================================

MARKET_CAP_LIMITS = {
    'large': 50000_00_00_000,     # > ₹50,000 Cr
    'mid': 10000_00_00_000,       # ₹10,000 - ₹50,000 Cr
    # < ₹10,000 Cr = small cap
}


# ==============================================================================
# TECHNICAL INDICATORS
# ==============================================================================

TECHNICAL_SETTINGS = {
    'rsi_period': 14,
    'rsi_oversold': 30,
    'support_window': 30,
    'volume_lookback': 20,
}


# ==============================================================================
# API SETTINGS
# ==============================================================================

API_SETTINGS = {
    'yfinance_timeout': 10,
    'request_delay': 0.5,          # Delay between API calls (seconds)
    'max_retries': 3,
}


# ==============================================================================
# DISPLAY SETTINGS
# ==============================================================================

DISPLAY = {
    'show_debug_info': False,
    'show_estimated_warnings': True,
    'decimal_places': 2,
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_pe_score(pe_ratio: float) -> tuple[int, str]:
    """
    Get P/E ratio score and assessment
    
    Args:
        pe_ratio: Price-to-Earnings ratio
    
    Returns:
        Tuple of (score, assessment)
    """
    if pe_ratio <= 0:
        return (2, "No Data")
    
    if pe_ratio < PE_THRESHOLDS['undervalued']:
        return (4, "Undervalued")
    elif pe_ratio < PE_THRESHOLDS['fair']:
        return (3, "Fair")
    elif pe_ratio < PE_THRESHOLDS['acceptable']:
        return (2, "Acceptable")
    elif pe_ratio < PE_THRESHOLDS['expensive']:
        return (1, "Expensive")
    else:
        return (0, "Overvalued")


def adjust_threshold_for_estimates(base_threshold: int, num_estimates: int) -> int:
    """
    Adjust quality threshold based on number of estimated fields
    
    Args:
        base_threshold: Base minimum score threshold
        num_estimates: Number of estimated fields
    
    Returns:
        Adjusted threshold
    """
    if not DATA_QUALITY['adjust_score_for_estimates']:
        return base_threshold
    
    if num_estimates >= DATA_QUALITY['max_estimated_fields']:
        return max(8, base_threshold - 2)
    
    return base_threshold


def get_market_cap_category(market_cap: float) -> str:
    """
    Categorize stock by market cap
    
    Args:
        market_cap: Market capitalization in ₹
    
    Returns:
        Category: 'large', 'mid', or 'small'
    """
    if market_cap >= MARKET_CAP_LIMITS['large']:
        return 'large'
    elif market_cap >= MARKET_CAP_LIMITS['mid']:
        return 'mid'
    else:
        return 'small'


# ==============================================================================
# CONFIGURATION VALIDATION
# ==============================================================================

def validate_config():
    """Validate configuration settings"""
    assert QUALITY_THRESHOLDS['min_fundamental_score'] <= 20, "Min score cannot exceed 20"
    assert QUALITY_THRESHOLDS['max_pe_ratio'] > 0, "Max P/E must be positive"
    assert POSITION_LIMITS['max_per_stock'] <= 1.0, "Max position cannot exceed 100%"
    assert all(0 < v <= 100 for v in DIP_THRESHOLDS.values()), "Thresholds must be 0-100"
    print("✅ Configuration validated successfully")


if __name__ == "__main__":
    # Validate configuration when run directly
    validate_config()
    
    # Display current settings
    print("\n📊 Current Configuration:")
    print("="*80)
    print(f"\nFundamental Defaults: {FUNDAMENTAL_DEFAULTS}")
    print(f"\nP/E Thresholds: {PE_THRESHOLDS}")
    print(f"\nQuality Thresholds: {QUALITY_THRESHOLDS}")
    print(f"\nDip Thresholds: {DIP_THRESHOLDS}")

