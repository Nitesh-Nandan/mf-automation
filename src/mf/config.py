"""
Mutual Fund Dip Analyzer Configuration
Centralized settings for thresholds and scoring parameters

SCORING SYSTEM (Total: 100 points):
------------------------------------
1. Dip Depth         : 40 points (40%) ⭐ PRIMARY SIGNAL
2. Historical Context: 13 points (13%)
3. Mean Reversion    : 13 points (13%)
4. Volatility        : 11 points (11%)
5. Recovery Speed    : 13 points (13%)
6. Fund Category     : 10 points (10%)

PHILOSOPHY:
- Dip Depth is the DOMINANT signal (40% weight)
- Other factors are quality filters (60% combined)
- Deep dips will ALWAYS trigger with minimal secondary support
- Conservative threshold: 60 points (1-2 signals/year)
- Historical data: 2 years (captures market cycles + price appreciation)
- Validated against real market corrections (Sept 2024: scores 78-97)
"""

# ==============================================================================
# ANALYSIS TIME WINDOWS
# ==============================================================================

TIME_WINDOWS = {
    "current_analysis_days": 180,  # 6 months for current dip analysis (catches full depth)
    "historical_analysis_days": 730,  # 2 years for historical context (captures market cycles + price appreciation)
    "min_dip_threshold": 8.0,  # Minimum 8% to consider (top 10% dips)
}


# ==============================================================================
# FACTOR 1: DIP DEPTH SCORING (0-40 points) ⭐ PRIMARY SIGNAL
# ==============================================================================
# DOMINANT factor at 40 points (40% weight)
# Deep dips will trigger with minimal secondary support

DIP_DEPTH_THRESHOLDS = {
    18: 40,  # ≥18% dip → 40 points (maximum - excellent opportunity!)
    15: 30,  # ≥15% dip → 30 points (very good)
    12: 25,  # ≥12% dip → 25 points (good)
    10: 22,  # ≥10% dip → 22 points (decent)
    8: 20,  # ≥8% dip  → 20 points (minimum threshold)
    # < 8%    → 0 points
}


# ==============================================================================
# FACTOR 2: HISTORICAL CONTEXT SCORING (0-13 points)
# ==============================================================================
# Rebalanced to 13 points to prioritize dip depth

HISTORICAL_CONTEXT = {
    "optimal_ratio_min": 50,  # Best entry: 50-80% of max historical dip (more realistic)
    "optimal_ratio_max": 80,
    "optimal_score": 13,  # Reduced from 15
    "thresholds": {
        (80, 90): 12,  # 80-90% of max
        (60, 80): 12,  # 60-80% of max (widened optimal range)
        (50, 60): 10,  # 50-60% of max
        (40, 50): 8,  # 40-50% of max
        (30, 40): 6,  # 30-40% of max
        (90, 100): 10,  # 90-100% of max (NEW or equal to historical max) - generous
    },
    "default_score": 4,  # <30% of max
    "no_data_score": 10,  # No/limited historical data available - generous default
}


# ==============================================================================
# FACTOR 3: MEAN REVERSION SCORING (0-13 points)
# ==============================================================================
# Rebalanced to 13 points to prioritize dip depth

MEAN_REVERSION = {
    "points_per_percent": 2,  # 2 points for each 1% below mean
    "max_score": 13,  # Maximum 13 points (reduced from 15)
    "above_mean_score": 0,  # No points if above mean
}


# ==============================================================================
# FACTOR 4: VOLATILITY SCORING (0-11 points)
# ==============================================================================
# Rebalanced to 11 points to prioritize dip depth

VOLATILITY_THRESHOLDS = {
    "sweet_spot_min": 8,  # Ideal volatility range
    "sweet_spot_max": 25,  # Expanded to match typical MF volatility
    "sweet_spot_score": 11,  # Reduced from 12
    "acceptable_max": 35,  # Expanded threshold
    "acceptable_score": 9,  # Reduced from 10
    "low_volatility_score": 7,  # < 8% volatility (reduced from 8)
    "high_volatility_score": 5,  # > 35% volatility (kept at 5)
}


# ==============================================================================
# FACTOR 5: RECOVERY SPEED SCORING (0-13 points)
# ==============================================================================
# Reduced from 15 to 13 points (rebalanced to give dip depth more weight)

RECOVERY_SPEED = {
    "min_dip_threshold": 8.0,  # Track dips ≥8% (matches main threshold)
    "thresholds": {
        30: 13,  # Avg recovery ≤30 days → 13 points (excellent) - reduced from 15
        60: 10,  # Avg recovery ≤60 days → 10 points (good) - reduced from 12
        90: 7,  # Avg recovery ≤90 days → 7 points (moderate) - reduced from 9
        # >90 days → 4 points (slow)
    },
    "slow_recovery_score": 4,  # >90 days recovery - reduced from 5
    "no_history_score": 8,  # No recovery data available - reduced from 9
}


# ==============================================================================
# FACTOR 6: FUND CATEGORY SCORING (0-10 points)
# ==============================================================================

FUND_CATEGORY_SCORES = {
    "Small Cap": 10,  # Highest volatility → most opportunity
    "Mid Cap": 8,  # Good volatility
    "Flexi Cap": 8,  # Mixed allocation - high flexibility
    "Large Cap": 6,  # Lower volatility but stable
    "Sectoral": 7,  # Sector-specific
    "Thematic": 7,  # Theme-based
    "Debt/Liquid": 3,  # Stable, minimal dip-buying benefit
    "Default": 7,  # Unknown category - neutral
}


# ==============================================================================
# RECOMMENDATION THRESHOLDS
# ==============================================================================
# Optimized thresholds (dip depth is dominant at 40%)

RECOMMENDATION_THRESHOLDS = {
    "ultra_conservative": 75,  # Very selective (bear markets, crashes) - 18%+ dips only
    "conservative": 60,  # Default - high quality only (1-2 signals/year) ⭐ LOWERED from 65
    "moderate": 55,  # Balanced approach (3-5 signals/year)
    "aggressive": 45,  # More opportunities (6-10 signals/year)
}


# ==============================================================================
# SCORING BANDS FOR RECOMMENDATIONS
# ==============================================================================
# Optimized for dip depth dominance (40% weight)

SCORING_BANDS = [
    (85, "STRONG BUY", 0.50, "Very High"),  # 85-100: Elite opportunities (18%+ dips)
    (75, "STRONG BUY", 0.40, "Very High"),  # 75-84: Excellent (15-18% dips)
    (60, "BUY", 0.30, "High"),  # 60-74: Good entry (12-15% dips, conservative) ⭐
    (55, "MODERATE BUY", 0.20, "Medium"),  # 55-59: Consider (10-12% dips, moderate)
    (45, "WEAK BUY", 0.15, "Low"),  # 45-54: Marginal (8-10% dips, aggressive)
    (0, "HOLD", 0.00, "None"),  # 0-44: No opportunity
]


# ==============================================================================
# POSITION SIZING
# ==============================================================================

POSITION_LIMITS = {
    "max_per_fund": 0.30,  # Max 30% in single fund
    "min_investment": 5000,  # Minimum ₹5000 per fund
    "reserve_for_opportunity": 0.20,  # Keep 20% for future dips
}


# ==============================================================================
# API SETTINGS
# ==============================================================================

API_SETTINGS = {
    "base_url": "https://api.mfapi.in/mf/",
    "timeout": 10,
    "retry_count": 3,
}


# ==============================================================================
# DISPLAY SETTINGS
# ==============================================================================

DISPLAY = {
    "decimal_places": 2,
    "show_score_breakdown": True,
    "show_detailed_analysis": True,
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
        Score (0-40 points)
    """
    for threshold in sorted(DIP_DEPTH_THRESHOLDS.keys(), reverse=True):
        if dip_percentage >= threshold:
            return DIP_DEPTH_THRESHOLDS[threshold]
    return 0


def get_historical_context_score(
    current_dip: float, max_historical_dip: float
) -> tuple[int, float]:
    """
    Calculate historical context score

    Args:
        current_dip: Current dip percentage
        max_historical_dip: Maximum historical dip

    Returns:
        Tuple of (score, ratio)
    """
    if max_historical_dip <= 0:
        return (HISTORICAL_CONTEXT["no_data_score"], 0.0)

    ratio = (current_dip / max_historical_dip) * 100

    # Check optimal range
    if (
        HISTORICAL_CONTEXT["optimal_ratio_min"]
        <= ratio
        <= HISTORICAL_CONTEXT["optimal_ratio_max"]
    ):
        return (HISTORICAL_CONTEXT["optimal_score"], ratio)

    # Special case: ratio >= 100 (current dip equals or exceeds historical max)
    # This happens when there's limited historical data or this is a new record dip
    if ratio >= 100:
        return (HISTORICAL_CONTEXT["no_data_score"], ratio)

    # Check other thresholds
    for (min_val, max_val), score in HISTORICAL_CONTEXT["thresholds"].items():
        if min_val <= ratio < max_val:
            return (score, ratio)

    return (HISTORICAL_CONTEXT["default_score"], ratio)


def get_mean_reversion_score(
    current_nav: float, mean_nav: float
) -> tuple[float, float]:
    """
    Calculate mean reversion score

    Args:
        current_nav: Current NAV
        mean_nav: Mean NAV

    Returns:
        Tuple of (score, deviation_percentage)
    """
    if current_nav >= mean_nav:
        return (MEAN_REVERSION["above_mean_score"], 0.0)

    deviation = ((mean_nav - current_nav) / mean_nav) * 100
    score = min(
        deviation * MEAN_REVERSION["points_per_percent"], MEAN_REVERSION["max_score"]
    )

    return (score, deviation)


def get_volatility_score(volatility: float) -> int:
    """
    Calculate volatility score

    Args:
        volatility: Annualized volatility (%)

    Returns:
        Score (0-11 points)
    """
    sweet_min = VOLATILITY_THRESHOLDS["sweet_spot_min"]
    sweet_max = VOLATILITY_THRESHOLDS["sweet_spot_max"]
    accept_max = VOLATILITY_THRESHOLDS["acceptable_max"]

    if sweet_min <= volatility <= sweet_max:
        return VOLATILITY_THRESHOLDS["sweet_spot_score"]
    elif sweet_max < volatility <= accept_max:
        return VOLATILITY_THRESHOLDS["acceptable_score"]
    elif volatility < sweet_min:
        return VOLATILITY_THRESHOLDS["low_volatility_score"]
    else:
        return VOLATILITY_THRESHOLDS["high_volatility_score"]


def get_recovery_speed_score(avg_recovery_days: float, has_history: bool) -> int:
    """
    Calculate recovery speed score

    Args:
        avg_recovery_days: Average days to recover from dips
        has_history: Whether historical data exists

    Returns:
        Score (0-13 points)
    """
    if not has_history:
        return RECOVERY_SPEED["no_history_score"]

    for threshold in sorted(RECOVERY_SPEED["thresholds"].keys()):
        if avg_recovery_days <= threshold:
            return RECOVERY_SPEED["thresholds"][threshold]

    # If recovery takes more than 90 days, give slow recovery score
    return RECOVERY_SPEED["slow_recovery_score"]


def get_fund_category_score(fund_type: str) -> int:
    """
    Get score based on fund category

    Args:
        fund_type: Type of fund

    Returns:
        Score (0-10 points)
    """
    return FUND_CATEGORY_SCORES.get(fund_type, FUND_CATEGORY_SCORES["Default"])


def get_recommendation(total_score: float, mode: str) -> tuple[bool, str, float, str]:
    """
    Generate recommendation based on score and mode

    Args:
        total_score: Total score (0-100)
        mode: Risk mode

    Returns:
        Tuple of (triggers_buy, recommendation, allocation, confidence)
    """
    threshold = RECOMMENDATION_THRESHOLDS.get(
        mode, RECOMMENDATION_THRESHOLDS["conservative"]
    )
    triggers_buy = total_score >= threshold

    for min_score, rec, allocation, confidence in SCORING_BANDS:
        if total_score >= min_score:
            return (triggers_buy, rec, allocation, confidence)

    return (False, "HOLD", 0.0, "Low")


# ==============================================================================
# CONFIGURATION VALIDATION
# ==============================================================================


def validate_config():
    """Validate configuration settings"""
    assert TIME_WINDOWS["current_analysis_days"] > 0, "Analysis days must be positive"
    assert (
        MEAN_REVERSION["points_per_percent"] > 0
    ), "Points per percent must be positive"
    assert all(
        v >= 0 for v in RECOMMENDATION_THRESHOLDS.values()
    ), "Thresholds must be non-negative"
    print("✅ MF Configuration validated successfully")
