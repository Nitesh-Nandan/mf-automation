"""
Technical Scoring Module for Stock Dip Analysis

Implements the 6-factor scoring system with configuration and calculation functions.
Clean, testable scoring functions for each factor.
"""

from typing import List, Dict
from .models import (
    OHLCVData,
    DipDepthScore,
    HistoricalContextScore,
    MeanReversionScore,
    VolatilityScore,
    RecoverySpeedScore,
    TechnicalScore,
)


# ============================================================================
# CONFIGURATION: Factor 1 - Dip Depth (0-20 points)
# ============================================================================

DIP_DEPTH_THRESHOLDS = {
    20: 20,  # >=20% dip → 20 points (Crash opportunity)
    15: 18,  # >=15% dip → 18 points (Excellent)
    12: 15,  # >=12% dip → 15 points (Very Good)
    10: 12,  # >=10% dip → 12 points (Good)
    8: 8,  # >=8% dip → 8 points (Moderate)
    5: 5,  # >=5% dip → 5 points (Minor)
    # < 5% → 0 points
}


def score_dip_depth(dip_percentage: float) -> DipDepthScore:
    """
    Factor 1: Score based on dip depth from 90-day peak

    Args:
        dip_percentage: Absolute percentage dip from peak (positive number)

    Returns:
        DipDepthScore with score and details
    """
    score = 0
    for threshold in sorted(DIP_DEPTH_THRESHOLDS.keys(), reverse=True):
        if dip_percentage >= threshold:
            score = DIP_DEPTH_THRESHOLDS[threshold]
            break

    return {
        "score": float(score),
        "dip_percentage": round(dip_percentage, 2),
        "max_score": 20,
    }


# ============================================================================
# CONFIGURATION: Factor 2 - Historical Context (0-25 points)
# ============================================================================

HISTORICAL_CONTEXT_THRESHOLDS = {
    0.90: 25,  # >=90% of max historical dip (Rare!)
    0.75: 20,  # >=75% of max (Significant)
    0.60: 15,  # >=60% of max (Above average)
    0.40: 10,  # >=40% of max (Average)
    0.20: 5,  # >=20% of max (Minor)
    # < 20% → 0 points
}

HISTORICAL_NO_DATA_SCORE = 10  # Default when no historical data


def score_historical_context(
    current_dip: float, max_historical_dip: float
) -> HistoricalContextScore:
    """
    Factor 2: Score based on current dip vs historical maximum

    Args:
        current_dip: Current dip percentage
        max_historical_dip: Maximum historical dip over 2 years

    Returns:
        HistoricalContextScore with score and details
    """
    if max_historical_dip <= 0:
        return {
            "score": float(HISTORICAL_NO_DATA_SCORE),
            "dip_ratio": 0.0,
            "max_historical_dip": 0.0,
            "max_score": 25,
        }

    ratio = current_dip / max_historical_dip
    score = 0

    for threshold in sorted(HISTORICAL_CONTEXT_THRESHOLDS.keys(), reverse=True):
        if ratio >= threshold:
            score = HISTORICAL_CONTEXT_THRESHOLDS[threshold]
            break

    return {
        "score": float(score),
        "dip_ratio": round(ratio, 2),
        "max_historical_dip": round(max_historical_dip, 2),
        "max_score": 25,
    }


# ============================================================================
# CONFIGURATION: Factor 3 - Mean Reversion (0-15 points) - 100 DMA
# ============================================================================


def score_mean_reversion(current_price: float, dma_100: float) -> MeanReversionScore:
    """
    Factor 3: Score based on distance from 100 DMA

    Args:
        current_price: Current stock price
        dma_100: 100-day moving average

    Returns:
        MeanReversionScore with score and details
    """
    if dma_100 <= 0:
        return {"score": 0.0, "distance_from_dma": 0.0, "dma_100": 0.0, "max_score": 15}

    distance = ((current_price - dma_100) / dma_100) * 100

    # Scoring based on distance
    if -6 <= distance < 0:
        score = 15  # Sweet spot (below 100 DMA)
    elif 0 <= distance <= 3:
        score = 12  # At 100 DMA support
    elif -12 <= distance < -6:
        score = 8  # Deep below (caution zone)
    elif 3 < distance <= 6:
        score = 5  # Slight premium
    elif 6 < distance <= 10:
        score = 2  # Moderately above
    else:
        score = 0  # Too high or falling knife (< -12%)

    return {
        "score": float(score),
        "distance_from_dma": round(distance, 2),
        "dma_100": round(dma_100, 2),
        "max_score": 15,
    }


# ============================================================================
# CONFIGURATION: Factor 4 - Volatility (0-10 points) - Relative Scoring
# ============================================================================

VOLATILITY_THRESHOLDS = {
    (0.85, 1.15): 10,  # Normal range (healthy dip)
    (0.70, 0.85): 8,  # Quieter than usual
    (1.15, 1.40): 6,  # Moderate spike
    (1.40, 1.75): 3,  # High spike (caution)
}


def score_volatility(
    volatility_current: float, volatility_baseline: float
) -> VolatilityScore:
    """
    Factor 4: Score based on current vs baseline volatility

    Args:
        volatility_current: Recent volatility (90 days, annualized %)
        volatility_baseline: Historical average volatility (2 years, annualized %)

    Returns:
        VolatilityScore with score and details
    """
    if volatility_baseline <= 0:
        return {
            "score": 5.0,
            "vol_ratio": 1.0,
            "current_vol": round(volatility_current, 2),
            "baseline_vol": 0.0,
            "max_score": 10,
        }

    vol_ratio = volatility_current / volatility_baseline
    score = 0

    # Check thresholds
    for (min_ratio, max_ratio), points in VOLATILITY_THRESHOLDS.items():
        if min_ratio <= vol_ratio <= max_ratio:
            score = points
            break

    # Special cases
    if vol_ratio > 1.75:
        score = 0  # Extreme spike (falling knife)
    elif vol_ratio < 0.70:
        score = 5  # Too quiet (slow bleed)

    return {
        "score": float(score),
        "vol_ratio": round(vol_ratio, 2),
        "current_vol": round(volatility_current, 2),
        "baseline_vol": round(volatility_baseline, 2),
        "max_score": 10,
    }


# ============================================================================
# CONFIGURATION: Factor 5 - Recovery Speed (0-20 points)
# ============================================================================

RECOVERY_SPEED_THRESHOLDS = {
    20: 20,  # < 20 days recovery → 20 points (Rocket)
    40: 15,  # < 40 days → 15 points (Fast)
    60: 10,  # < 60 days → 10 points (Moderate)
    90: 5,  # < 90 days → 5 points (Slow)
    # > 90 days → 0 points (Sluggish)
}

RECOVERY_NO_DATA_SCORE = 10  # Default when no recovery history


def score_recovery_speed(
    avg_recovery_days: float, recovery_count: int
) -> RecoverySpeedScore:
    """
    Factor 5: Score based on historical recovery speed

    Args:
        avg_recovery_days: Average days to recover from significant dips
        recovery_count: Number of recovery events tracked

    Returns:
        RecoverySpeedScore with score and details
    """
    if recovery_count == 0:
        return {
            "score": float(RECOVERY_NO_DATA_SCORE),
            "avg_recovery_days": 0.0,
            "recovery_count": 0,
            "max_score": 20,
        }

    score = 0
    for threshold in sorted(RECOVERY_SPEED_THRESHOLDS.keys()):
        if avg_recovery_days < threshold:
            score = RECOVERY_SPEED_THRESHOLDS[threshold]
            break

    return {
        "score": float(score),
        "avg_recovery_days": round(avg_recovery_days, 1),
        "recovery_count": recovery_count,
        "max_score": 20,
    }


# ============================================================================
# CONFIGURATION: Factor 6 - Technicals (0-10 points)
# ============================================================================

# RSI Thresholds
RSI_THRESHOLDS = {
    40: 5,  # RSI < 40 → 5 points (Oversold)
    50: 3,  # RSI 40-50 → 3 points (Accumulation)
    60: 1,  # RSI 50-60 → 1 point (Neutral)
    # RSI > 60 → 0 points (Momentum)
}

# Volume Thresholds
VOLUME_SPIKE_THRESHOLDS = {
    2.0: 3,  # > 2x average → 3 points (Capitulation)
    1.5: 2,  # > 1.5x average → 2 points (Elevated)
    # < 1.5x → 0 points
}


def score_technicals(
    rsi: float,
    volume_ratio: float,
    distance_50dma_pct: float,
    distance_100dma_pct: float,
) -> TechnicalScore:
    """
    Factor 6: Score based on RSI, Volume, and Support levels

    Args:
        rsi: RSI indicator value (0-100)
        volume_ratio: Current volume / 20-day average
        distance_50dma_pct: % distance from 50 DMA
        distance_100dma_pct: % distance from 100 DMA

    Returns:
        TechnicalScore with score and details
    """
    # RSI scoring (0-5 pts)
    rsi_score = 0
    if rsi < 40:
        rsi_score = 5
    elif rsi < 50:
        rsi_score = 3
    elif rsi < 60:
        rsi_score = 1

    # Volume spike scoring (0-3 pts)
    volume_score = 0
    if volume_ratio > 2.0:
        volume_score = 3
    elif volume_ratio > 1.5:
        volume_score = 2

    # Bull market support scoring (0-2 pts)
    support_score = 0
    if abs(distance_50dma_pct) <= 2:
        support_score = 1  # Near 50 DMA
    elif abs(distance_100dma_pct) <= 3:
        support_score = 2  # Near 100 DMA

    total_score = rsi_score + volume_score + support_score

    return {
        "score": float(total_score),
        "rsi": round(rsi, 2),
        "rsi_score": float(rsi_score),
        "volume_ratio": round(volume_ratio, 2),
        "volume_score": float(volume_score),
        "support_score": float(support_score),
        "max_score": 10,
    }


# ============================================================================
# RECOMMENDATION LOGIC
# ============================================================================

RECOMMENDATION_THRESHOLDS = {
    85: ("STRONG BUY", 1.0),
    75: ("BUY", 0.75),
    60: ("ACCUMULATE", 0.50),
    50: ("NIBBLE", 0.25),
    0: ("WAIT", 0.0),
}


def get_recommendation(total_score: float) -> tuple[str, float]:
    """
    Generate recommendation based on total score

    Args:
        total_score: Total score (0-100)

    Returns:
        Tuple of (recommendation, position_multiplier)
    """
    for threshold in sorted(RECOMMENDATION_THRESHOLDS.keys(), reverse=True):
        if total_score >= threshold:
            return RECOMMENDATION_THRESHOLDS[threshold]

    return ("WAIT", 0.0)
