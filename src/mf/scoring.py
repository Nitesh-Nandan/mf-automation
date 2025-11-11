"""
Scoring Module for Mutual Fund Dip Analysis
Clean, testable scoring functions for each factor
"""

import statistics
from datetime import datetime
from typing import Dict, List

from config import (
    get_dip_depth_score,
    get_historical_context_score,
    get_mean_reversion_score,
    get_volatility_score,
    get_recovery_speed_score,
    get_fund_category_score,
    RECOVERY_SPEED
)


def calculate_volatility(nav_data: List[Dict]) -> float:
    """
    Calculate annualized volatility of NAV returns
    
    Formula: Standard Deviation of Daily Returns × √252 × 100
    Where 252 = typical trading days per year
    
    Args:
        nav_data: List of {date, nav} dictionaries
    
    Returns:
        Annualized volatility as percentage
    """
    if len(nav_data) < 2:
        return 0.0
    
    returns = []
    for i in range(1, len(nav_data)):
        daily_return = (nav_data[i]['nav'] - nav_data[i-1]['nav']) / nav_data[i-1]['nav']
        returns.append(daily_return)
    
    if not returns:
        return 0.0
    
    volatility = statistics.stdev(returns) * (252 ** 0.5) * 100
    return volatility


def calculate_recovery_speed(nav_data: List[Dict]) -> Dict:
    """
    Analyze historical recovery speed from dips
    
    Tracks all 5%+ dips and measures days to full recovery
    
    Args:
        nav_data: List of {date, nav} dictionaries
    
    Returns:
        Dictionary with:
        - avg_recovery_days: Average days to recover
        - recovery_count: Number of recoveries tracked
        - has_history: Whether recovery data exists
    """
    nav_data_sorted = sorted(nav_data, key=lambda x: x['date'])
    
    min_dip_threshold = RECOVERY_SPEED['min_dip_threshold']
    
    recoveries = []
    in_dip = False
    dip_start_idx = 0
    peak_nav = nav_data_sorted[0]['nav']
    
    for i, entry in enumerate(nav_data_sorted):
        current_nav = entry['nav']
        
        # Check if new peak reached
        if current_nav > peak_nav:
            # If recovering from a dip, record recovery time
            if in_dip and i > dip_start_idx:
                recovery_days = (entry['date'] - nav_data_sorted[dip_start_idx]['date']).days
                recoveries.append(recovery_days)
                in_dip = False
            peak_nav = current_nav
        
        # Check if entering a dip
        dip_pct = ((peak_nav - current_nav) / peak_nav) * 100
        if dip_pct >= min_dip_threshold and not in_dip:
            in_dip = True
            dip_start_idx = i
    
    if recoveries:
        avg_recovery = sum(recoveries) / len(recoveries)
        return {
            'avg_recovery_days': avg_recovery,
            'recovery_count': len(recoveries),
            'has_history': True
        }
    
    return {
        'avg_recovery_days': 0,
        'recovery_count': 0,
        'has_history': False
    }


def score_factor_1_dip_depth(current_dip: float) -> Dict:
    """
    Factor 1: Dip Depth Scoring (0-25 points)
    
    Args:
        current_dip: Current dip from peak (%)
    
    Returns:
        Dictionary with score and details
    """
    score = get_dip_depth_score(current_dip)
    
    return {
        'score': score,
        'value': current_dip,
        'max': 25,
        'factor': 'Dip Depth'
    }


def score_factor_2_historical_context(
    current_dip: float,
    max_historical_dip: float
) -> Dict:
    """
    Factor 2: Historical Context Scoring (0-20 points)
    
    Args:
        current_dip: Current dip percentage
        max_historical_dip: Maximum historical dip
    
    Returns:
        Dictionary with score and details
    """
    score, ratio = get_historical_context_score(current_dip, max_historical_dip)
    
    return {
        'score': score,
        'current_vs_max_ratio': round(ratio, 2),
        'max': 20,
        'factor': 'Historical Context'
    }


def score_factor_3_mean_reversion(
    current_nav: float,
    mean_nav: float
) -> Dict:
    """
    Factor 3: Mean Reversion Scoring (0-15 points)
    
    Args:
        current_nav: Current NAV
        mean_nav: Mean NAV
    
    Returns:
        Dictionary with score and details
    """
    score, deviation = get_mean_reversion_score(current_nav, mean_nav)
    
    return {
        'score': round(score, 2),
        'below_mean_pct': round(deviation, 2),
        'max': 15,
        'factor': 'Mean Reversion'
    }


def score_factor_4_volatility(volatility: float) -> Dict:
    """
    Factor 4: Volatility Scoring (0-15 points)
    
    Args:
        volatility: Annualized volatility (%)
    
    Returns:
        Dictionary with score and details
    """
    score = get_volatility_score(volatility)
    
    return {
        'score': score,
        'volatility': round(volatility, 2),
        'max': 15,
        'factor': 'Volatility'
    }


def score_factor_5_recovery_speed(recovery_data: Dict) -> Dict:
    """
    Factor 5: Recovery Speed Scoring (0-15 points)
    
    Args:
        recovery_data: Dictionary from calculate_recovery_speed()
    
    Returns:
        Dictionary with score and details
    """
    score = get_recovery_speed_score(
        recovery_data['avg_recovery_days'],
        recovery_data['has_history']
    )
    
    return {
        'score': score,
        'avg_recovery_days': round(recovery_data['avg_recovery_days'], 1),
        'recovery_count': recovery_data['recovery_count'],
        'max': 15,
        'factor': 'Recovery Speed'
    }


def score_factor_6_fund_category(fund_type: str) -> Dict:
    """
    Factor 6: Fund Category Scoring (0-10 points)
    
    Args:
        fund_type: Type of fund
    
    Returns:
        Dictionary with score and details
    """
    score = get_fund_category_score(fund_type)
    
    return {
        'score': score,
        'category': fund_type,
        'max': 10,
        'factor': 'Fund Category'
    }


def calculate_all_scores(
    current_analysis: Dict,
    historical_analysis: Dict,
    nav_data: List[Dict],
    fund_type: str
) -> tuple[Dict, float]:
    """
    Calculate all 6 factor scores
    
    Args:
        current_analysis: Current dip analysis data
        historical_analysis: Historical dip analysis data
        nav_data: Full NAV history
        fund_type: Fund category
    
    Returns:
        Tuple of (score_breakdown dict, total_score)
    """
    score_breakdown = {}
    
    # Factor 1: Dip Depth
    score_breakdown['dip_depth'] = score_factor_1_dip_depth(
        current_analysis['dip_from_peak_percentage']
    )
    
    # Factor 2: Historical Context
    score_breakdown['historical_context'] = score_factor_2_historical_context(
        current_analysis['dip_from_peak_percentage'],
        historical_analysis['max_historical_dip']
    )
    
    # Factor 3: Mean Reversion
    score_breakdown['mean_reversion'] = score_factor_3_mean_reversion(
        current_analysis['current_nav'],
        current_analysis['mean_nav']
    )
    
    # Factor 4: Volatility
    volatility = calculate_volatility(nav_data)
    score_breakdown['volatility'] = score_factor_4_volatility(volatility)
    
    # Factor 5: Recovery Speed
    recovery_data = calculate_recovery_speed(nav_data)
    score_breakdown['recovery_speed'] = score_factor_5_recovery_speed(recovery_data)
    
    # Factor 6: Fund Category
    score_breakdown['fund_category'] = score_factor_6_fund_category(fund_type)
    
    # Calculate total
    total_score = sum(factor['score'] for factor in score_breakdown.values())
    
    return (score_breakdown, total_score)

