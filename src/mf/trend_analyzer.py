"""
Trend Analyzer Module

Analyzes current NAV trends and dip patterns for mutual funds.
"""

from datetime import datetime
from typing import Dict, List, Optional

from .constants import DATE_FORMAT_API, ERROR_INSUFFICIENT_DATA
from .data_fetcher import fetch_nav_data
from .exceptions import InsufficientDataError
from .types import CurrentAnalysis, NAVEntry
from .utils import (
    calculate_dip_percentage,
    calculate_mean_nav,
    find_bottom_nav,
    find_peak_nav,
    safe_round,
)


def analyze_fund_dip(
    fund_name: str,
    code: str,
    dip_percentage: float = 10.0,
    days: int = 120,
    nav_data: Optional[List[NAVEntry]] = None,
) -> CurrentAnalysis:
    """
    Analyze if a mutual fund's current NAV is in a dip compared to its peak.

    Args:
        fund_name: Name of the mutual fund
        code: API code for the fund
        dip_percentage: Percentage dip to check for (default: 10%)
        days: Number of days to look back for historical data (default: 120)
        nav_data: Optional pre-fetched NAV data (optimization to avoid duplicate API calls)

    Returns:
        CurrentAnalysis dictionary containing analysis results

    Example:
        >>> result = analyze_fund_dip("Quant Small Cap", "120828", days=180)
        >>> print(f"Dip: {result['dip_from_peak_percentage']}%")
    """

    try:
        # Use pre-fetched data if provided, otherwise fetch from API
        if nav_data is not None:
            # Use last 'days' entries from pre-fetched data
            filtered_data = nav_data[-days:] if len(nav_data) > days else nav_data
        else:
            # Fetch NAV data using shared data fetcher
            filtered_data = fetch_nav_data(code, days=days)

        if not filtered_data:
            return {
                "fund_name": fund_name,
                "fund_code": code,
                "error": ERROR_INSUFFICIENT_DATA,
                # Dummy values to satisfy type
                "is_in_dip": False,
                "current_nav": 0.0,
                "current_date": "",
                "peak_nav": 0.0,
                "peak_date": "",
                "bottom_nav": 0.0,
                "bottom_date": "",
                "mean_nav": 0.0,
                "dip_from_peak_percentage": 0.0,
                "days_analyzed": 0,
            }  # type: ignore

        # Data comes pre-sorted ASCENDING (oldest first) from dip_analyzer
        # For backward compatibility (standalone calls), ensure sorted
        if nav_data is None:
            filtered_data.sort(key=lambda x: x["date"])

        # Current NAV (most recent = last entry in ascending order)
        current_entry = filtered_data[-1]
        current_nav = current_entry["nav"]
        current_date = current_entry["date"]

        # Find peak (highest) NAV and its date
        peak_entry = find_peak_nav(filtered_data)
        peak_nav = peak_entry["nav"]
        peak_date = peak_entry["date"]

        # Find bottom (lowest) NAV and its date
        bottom_entry = find_bottom_nav(filtered_data)
        bottom_nav = bottom_entry["nav"]
        bottom_date = bottom_entry["date"]

        # Calculate mean NAV
        mean_nav = calculate_mean_nav(filtered_data)

        # Calculate dip percentage from peak
        dip_from_peak_pct = calculate_dip_percentage(peak_nav, current_nav)

        # Check if it's in a dip
        is_in_dip = dip_from_peak_pct >= dip_percentage

        return {
            "fund_name": fund_name,
            "fund_code": code,
            "is_in_dip": is_in_dip,
            "current_nav": safe_round(current_nav, 4),
            "current_date": current_date.strftime(DATE_FORMAT_API),
            "peak_nav": safe_round(peak_nav, 4),
            "peak_date": peak_date.strftime(DATE_FORMAT_API),
            "bottom_nav": safe_round(bottom_nav, 4),
            "bottom_date": bottom_date.strftime(DATE_FORMAT_API),
            "mean_nav": safe_round(mean_nav, 4),
            "dip_from_peak_percentage": safe_round(dip_from_peak_pct, 2),
            "days_analyzed": len(filtered_data),
            "error": None,
        }  # type: ignore

    except Exception as e:
        return {
            "fund_name": fund_name,
            "fund_code": code,
            "error": f"Error analyzing fund: {str(e)}",
            # Dummy values to satisfy type
            "is_in_dip": False,
            "current_nav": 0.0,
            "current_date": "",
            "peak_nav": 0.0,
            "peak_date": "",
            "bottom_nav": 0.0,
            "bottom_date": "",
            "mean_nav": 0.0,
            "dip_from_peak_percentage": 0.0,
            "days_analyzed": 0,
        }  # type: ignore


def print_analysis_result(result: CurrentAnalysis) -> None:
    """
    Pretty print the analysis result.

    Args:
        result: CurrentAnalysis dictionary from analyze_fund_dip
    """
    from .constants import EMOJI_CHECK, EMOJI_CROSS, SEPARATOR_MINI
    from .utils import format_currency

    print("\n" + SEPARATOR_MINI)
    print(f"Fund Analysis: {result['fund_name']}")
    print(SEPARATOR_MINI)

    if result.get("error"):
        print(f"{EMOJI_CROSS} Error: {result['error']}")
        return

    print(f"Fund Code: {result['fund_code']}")
    print(f"Days Analyzed: {result['days_analyzed']}")
    print(
        f"\nCurrent NAV: {format_currency(result['current_nav'])} (as of {result['current_date']})"
    )
    print(f"Peak NAV: {format_currency(result['peak_nav'])} (on {result['peak_date']})")
    print(
        f"Bottom NAV: {format_currency(result['bottom_nav'])} (on {result['bottom_date']})"
    )
    print(f"Mean NAV: {format_currency(result['mean_nav'])}")
    print(f"\nDip from Peak: {result['dip_from_peak_percentage']}%")

    if result["is_in_dip"]:
        print(
            f"{EMOJI_CHECK} Fund is in a DIP (down {result['dip_from_peak_percentage']}% from peak)"
        )
    else:
        print(
            f"{EMOJI_CROSS} Fund is NOT in a significant dip (only {result['dip_from_peak_percentage']}% from peak)"
        )

    print(SEPARATOR_MINI)
