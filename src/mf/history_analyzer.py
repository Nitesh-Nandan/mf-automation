"""
History Analyzer Module

Analyzes historical NAV patterns and maximum dips for mutual funds.
"""

from datetime import datetime
from typing import Dict, List, Optional

from .constants import DATE_FORMAT_API, SEPARATOR_LINE
from .data_fetcher import fetch_nav_data
from .fund_loader import get_mf_funds
from .types import HistoricalAnalysis, NAVEntry
from .utils import (
    calculate_dip_percentage,
    calculate_mean_nav,
    find_bottom_nav,
    find_peak_nav,
    format_currency,
    safe_round,
)


def analyze_max_historical_dip(
    fund_name: str,
    code: str,
    days: int = 730,  # 2 years by default
    nav_data: Optional[List[NAVEntry]] = None,
) -> HistoricalAnalysis:
    """
    Analyze the maximum NAV dip that has occurred historically for a fund.

    Args:
        fund_name: Name of the fund
        code: API code for the fund
        days: Number of days to look back (default: 730 = 2 years)
        nav_data: Optional pre-fetched NAV data (optimization to avoid duplicate API calls)

    Returns:
        Dictionary containing max dip information and when it occurred
    """

    try:
        # Use pre-fetched data if provided, otherwise fetch from API
        if nav_data is None:
            nav_data = fetch_nav_data(code, days=days)

        if len(nav_data) < 2:
            return {
                "fund_name": fund_name,
                "fund_code": code,
                "error": "Not enough data",
            }

        # Data comes pre-sorted ASCENDING (oldest first) from dip_analyzer
        # For backward compatibility (standalone calls), ensure sorted
        if nav_data is None:
            nav_data.sort(key=lambda x: x["date"])

        # Calculate maximum dip by checking from each peak
        max_dip_percentage = 0
        max_dip_info = None

        # Track running maximum NAV and calculate dip from it
        running_max_nav = nav_data[0]["nav"]
        running_max_date = nav_data[0]["date"]

        for entry in nav_data:
            current_nav = entry["nav"]
            current_date = entry["date"]

            # Update running maximum
            if current_nav > running_max_nav:
                running_max_nav = current_nav
                running_max_date = current_date

            # Calculate dip from running maximum
            dip_percentage = ((running_max_nav - current_nav) / running_max_nav) * 100

            if dip_percentage > max_dip_percentage:
                max_dip_percentage = dip_percentage
                max_dip_info = {
                    "peak_nav": running_max_nav,
                    "peak_date": running_max_date,
                    "bottom_nav": current_nav,
                    "bottom_date": current_date,
                    "dip_percentage": dip_percentage,
                }

        # Get current NAV info
        current_entry = nav_data[-1]
        current_nav = current_entry["nav"]
        current_date = current_entry["date"]

        # Find peak (highest) NAV in the period
        peak_entry = find_peak_nav(nav_data)
        peak_nav = peak_entry["nav"]
        peak_date = peak_entry["date"]

        # Find bottom (lowest) NAV in the period - find absolute minimum
        bottom_entry = find_bottom_nav(nav_data)
        bottom_nav = bottom_entry["nav"]
        bottom_date = bottom_entry["date"]

        # Calculate mean NAV over the entire period
        mean_nav = calculate_mean_nav(nav_data)

        # Current dip from peak
        dip_from_peak_percentage = calculate_dip_percentage(peak_nav, current_nav)

        # Check if it's in a dip
        is_in_dip = dip_from_peak_percentage >= dip_percentage

        # Consistent return structure (same as trend_analyzer)
        return {
            "fund_name": fund_name,
            "fund_code": code,
            "days_analyzed": len(nav_data),
            "current_nav": safe_round(current_nav, 4),
            "current_date": current_date.strftime(DATE_FORMAT_API),
            "peak_nav": safe_round(peak_nav, 4),
            "peak_date": peak_date.strftime(DATE_FORMAT_API),
            "bottom_nav": safe_round(bottom_nav, 4),
            "bottom_date": bottom_date.strftime(DATE_FORMAT_API),
            "mean_nav": safe_round(mean_nav, 4),
            "dip_from_peak_percentage": safe_round(dip_from_peak_percentage, 2),
            "is_in_dip": is_in_dip,
            # Additional historical-specific fields
            "max_historical_dip": safe_round(max_dip_percentage, 2),
            "max_dip_info": {
                "peak_nav": safe_round(max_dip_info["peak_nav"], 4),
                "peak_date": max_dip_info["peak_date"].strftime(DATE_FORMAT_API),
                "bottom_nav": safe_round(max_dip_info["bottom_nav"], 4),
                "bottom_date": max_dip_info["bottom_date"].strftime(DATE_FORMAT_API),
                "dip_percentage": safe_round(max_dip_info["dip_percentage"], 2),
            },
            "has_10_percent_dip": max_dip_percentage >= 10.0,
            "error": None,
        }  # type: ignore

    except Exception as e:
        return {"fund_name": fund_name, "fund_code": code, "error": f"Error: {str(e)}"}
