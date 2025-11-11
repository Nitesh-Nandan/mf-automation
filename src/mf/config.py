"""
Mutual Fund Dip Analyzer Configuration
Centralized settings for thresholds and scoring parameters
"""

# ==============================================================================
# ANALYSIS TIME WINDOWS
# ==============================================================================

TIME_WINDOWS = {
    'current_analysis_days': 120,     # 4 months for current dip analysis
    'historical_analysis_days': 730,  # 2 years for historical context
    'min_dip_threshold': 5.0,         # Minimum % to consider a dip
}


# ==============================================================================
# FACTOR 1: DIP DEPTH SCORING (0-25 points)
# ==============================================================================

DIP_DEPTH_THRESHOLDS = {
    20: 25,  # ≥20% dip → 25 points
    15: 22,  # ≥15% dip → 22 points  
    12: 18,  # ≥12% dip → 18 points
    10: 15,  # ≥10% dip → 15 points
    7:  10,  # ≥7% dip  → 10 points
    5:  5,   # ≥5% dip  → 5 points
    # < 5%    → 0 points
}


# ==============================================================================
# FACTOR 2: HISTORICAL CONTEXT SCORING (0-20 points)
# ==============================================================================

HISTORICAL_CONTEXT = {
    'optimal_ratio_min': 60,  # Best entry: 60-80% of max historical dip
    'optimal_ratio_max': 80,
    'optimal_score': 20,
    
    'thresholds': {
        (80, 90): 18,   # 80-90% of max
        (50, 60): 15,   # 50-60% of max
        (40, 50): 10,   # 40-50% of max
        (90, 100): 12,  # 90%+ of max (caution - near bottom)
    },
    
    'default_score': 5,         # <40% of max
    'no_data_score': 10,        # No historical data available
}


# ==============================================================================
# FACTOR 3: MEAN REVERSION SCORING (0-15 points)
# ==============================================================================

MEAN_REVERSION = {
    'points_per_percent': 2,    # 2 points for each 1% below mean
    'max_score': 15,            # Maximum 15 points
    'above_mean_score': 0,      # No points if above mean
}


# ==============================================================================
# FACTOR 4: VOLATILITY SCORING (0-15 points)
# ==============================================================================

VOLATILITY_THRESHOLDS = {
    'sweet_spot_min': 8,        # Ideal volatility range
    'sweet_spot_max': 15,
    'sweet_spot_score': 15,
    
    'acceptable_max': 25,
    'acceptable_score': 12,
    
    'low_volatility_score': 10,  # 5-8% volatility
    'high_volatility_score': 5,  # >25% volatility
}


# ==============================================================================
# FACTOR 5: RECOVERY SPEED SCORING (0-15 points)
# ==============================================================================

RECOVERY_SPEED = {
    'min_dip_threshold': 5.0,   # Track dips ≥5%
    
    'thresholds': {
        30: 15,   # Avg recovery ≤30 days → 15 points (excellent)
        60: 12,   # Avg recovery ≤60 days → 12 points (good)
        90: 8,    # Avg recovery ≤90 days → 8 points (moderate)
        # >90 days → 4 points (slow)
    },
    
    'slow_recovery_score': 4,   # >90 days recovery
    'no_history_score': 8,      # No recovery data available (neutral)
}


# ==============================================================================
# FACTOR 6: FUND CATEGORY SCORING (0-10 points)
# ==============================================================================

FUND_CATEGORY_SCORES = {
    'Small Cap': 10,      # Highest volatility → most opportunity
    'Mid Cap': 8,         # Good volatility
    'Flexi Cap': 8,       # Mixed allocation - high flexibility
    'Large Cap': 6,       # Lower volatility but stable
    'Sectoral': 7,        # Sector-specific
    'Thematic': 7,        # Theme-based
    'Debt/Liquid': 3,     # Stable, minimal dip-buying benefit
    'Default': 7,         # Unknown category - neutral
}


# ==============================================================================
# RECOMMENDATION THRESHOLDS
# ==============================================================================

RECOMMENDATION_THRESHOLDS = {
    'ultra_conservative': 70,   # Very selective (bear markets, crashes)
    'conservative': 60,         # Default - high quality only (normal conditions) ⭐
    'moderate': 50,             # Balanced approach (bull markets with pullbacks)
    'aggressive': 40,           # More opportunities (strong bull runs)
}


# ==============================================================================
# SCORING BANDS FOR RECOMMENDATIONS
# ==============================================================================

SCORING_BANDS = [
    (80, 'STRONG BUY', 0.50, 'Very High'),    # 80-100: Deploy immediately
    (75, 'STRONG BUY', 0.40, 'Very High'),    # 75-79: Excellent opportunity
    (60, 'BUY', 0.30, 'High'),                # 60-74: Good entry point
    (45, 'MODERATE BUY', 0.20, 'Medium'),     # 45-59: Consider buying
    (30, 'WEAK BUY', 0.10, 'Low'),            # 30-44: Wait for better
    (0, 'HOLD', 0.00, 'None'),                # 0-29: No opportunity
]


# ==============================================================================
# POSITION SIZING
# ==============================================================================

POSITION_LIMITS = {
    'max_per_fund': 0.30,        # Max 30% in single fund
    'min_investment': 5000,      # Minimum ₹5000 per fund
    'reserve_for_opportunity': 0.20,  # Keep 20% for future dips
}


# ==============================================================================
# API SETTINGS
# ==============================================================================

API_SETTINGS = {
    'base_url': 'https://api.mfapi.in/mf/',
    'timeout': 10,
    'retry_count': 3,
}


# ==============================================================================
# DISPLAY SETTINGS
# ==============================================================================

DISPLAY = {
    'decimal_places': 2,
    'show_score_breakdown': True,
    'show_detailed_analysis': True,
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_dip_depth_score(dip_percentage: float) -> int:
    """
    Calculate dip depth score based on percentage
    
    Args:
        dip_percentage: Current dip from peak (%)
    
    Returns:
        Score (0-25 points)
    """
    for threshold in sorted(DIP_DEPTH_THRESHOLDS.keys(), reverse=True):
        if dip_percentage >= threshold:
            return DIP_DEPTH_THRESHOLDS[threshold]
    return 0


def get_historical_context_score(current_dip: float, max_historical_dip: float) -> tuple[int, float]:
    """
    Calculate historical context score
    
    Args:
        current_dip: Current dip percentage
        max_historical_dip: Maximum historical dip
    
    Returns:
        Tuple of (score, ratio)
    """
    if max_historical_dip <= 0:
        return (HISTORICAL_CONTEXT['no_data_score'], 0.0)
    
    ratio = (current_dip / max_historical_dip) * 100
    
    # Check optimal range
    if HISTORICAL_CONTEXT['optimal_ratio_min'] <= ratio <= HISTORICAL_CONTEXT['optimal_ratio_max']:
        return (HISTORICAL_CONTEXT['optimal_score'], ratio)
    
    # Check other thresholds
    for (min_val, max_val), score in HISTORICAL_CONTEXT['thresholds'].items():
        if min_val <= ratio < max_val:
            return (score, ratio)
    
    return (HISTORICAL_CONTEXT['default_score'], ratio)


def get_mean_reversion_score(current_nav: float, mean_nav: float) -> tuple[float, float]:
    """
    Calculate mean reversion score
    
    Args:
        current_nav: Current NAV
        mean_nav: Mean NAV
    
    Returns:
        Tuple of (score, deviation_percentage)
    """
    if current_nav >= mean_nav:
        return (MEAN_REVERSION['above_mean_score'], 0.0)
    
    deviation = ((mean_nav - current_nav) / mean_nav) * 100
    score = min(
        deviation * MEAN_REVERSION['points_per_percent'],
        MEAN_REVERSION['max_score']
    )
    
    return (score, deviation)


def get_volatility_score(volatility: float) -> int:
    """
    Calculate volatility score
    
    Args:
        volatility: Annualized volatility (%)
    
    Returns:
        Score (0-15 points)
    """
    sweet_min = VOLATILITY_THRESHOLDS['sweet_spot_min']
    sweet_max = VOLATILITY_THRESHOLDS['sweet_spot_max']
    accept_max = VOLATILITY_THRESHOLDS['acceptable_max']
    
    if sweet_min <= volatility <= sweet_max:
        return VOLATILITY_THRESHOLDS['sweet_spot_score']
    elif sweet_max < volatility <= accept_max:
        return VOLATILITY_THRESHOLDS['acceptable_score']
    elif volatility < sweet_min:
        return VOLATILITY_THRESHOLDS['low_volatility_score']
    else:
        return VOLATILITY_THRESHOLDS['high_volatility_score']


def get_recovery_speed_score(avg_recovery_days: float, has_history: bool) -> int:
    """
    Calculate recovery speed score
    
    Args:
        avg_recovery_days: Average days to recover from dips
        has_history: Whether historical data exists
    
    Returns:
        Score (0-15 points)
    """
    if not has_history:
        return RECOVERY_SPEED['no_history_score']
    
    for threshold in sorted(RECOVERY_SPEED['thresholds'].keys()):
        if avg_recovery_days <= threshold:
            return RECOVERY_SPEED['thresholds'][threshold]
    
    # If recovery takes more than 90 days, give slow recovery score
    return RECOVERY_SPEED['slow_recovery_score']


def get_fund_category_score(fund_type: str) -> int:
    """
    Get score based on fund category
    
    Args:
        fund_type: Type of fund
    
    Returns:
        Score (0-10 points)
    """
    return FUND_CATEGORY_SCORES.get(fund_type, FUND_CATEGORY_SCORES['Default'])


def get_recommendation(
    total_score: float,
    mode: str
) -> tuple[bool, str, float, str]:
    """
    Generate recommendation based on score and mode
    
    Args:
        total_score: Total score (0-100)
        mode: Risk mode
    
    Returns:
        Tuple of (triggers_buy, recommendation, allocation, confidence)
    """
    threshold = RECOMMENDATION_THRESHOLDS.get(mode, RECOMMENDATION_THRESHOLDS['conservative'])
    triggers_buy = total_score >= threshold
    
    for min_score, rec, allocation, confidence in SCORING_BANDS:
        if total_score >= min_score:
            return (triggers_buy, rec, allocation, confidence)
    
    return (False, 'HOLD', 0.0, 'Low')


# ==============================================================================
# CONFIGURATION VALIDATION
# ==============================================================================

def validate_config():
    """Validate configuration settings"""
    assert TIME_WINDOWS['current_analysis_days'] > 0, "Analysis days must be positive"
    assert MEAN_REVERSION['points_per_percent'] > 0, "Points per percent must be positive"
    assert all(v >= 0 for v in RECOMMENDATION_THRESHOLDS.values()), "Thresholds must be non-negative"
    print("✅ MF Configuration validated successfully")


if __name__ == "__main__":
    validate_config()
    
    print("\n📊 MF Configuration Summary:")
    print("="*80)
    print(f"\nTime Windows: {TIME_WINDOWS}")
    print(f"\nRecommendation Thresholds: {RECOMMENDATION_THRESHOLDS}")
    print(f"\nFund Categories: {FUND_CATEGORY_SCORES}")
    print(f"\nPosition Limits: {POSITION_LIMITS}")

