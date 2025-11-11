"""
Utility functions for Mutual Fund Analyzer

Common helper functions used across multiple modules.
"""

from datetime import datetime
from typing import Dict, List


def format_date_short(date_str: str) -> str:
    """
    Convert date from DD-MM-YYYY to DD-MMM-YY format

    Args:
        date_str: Date string in DD-MM-YYYY format

    Returns:
        Date string in DD-MMM-YY format (e.g., "03-Mar-25")

    Example:
        >>> format_date_short("03-03-2025")
        "03-Mar-25"
    """
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime("%d-%b-%y")
    except (ValueError, AttributeError):
        return date_str  # Return original if parsing fails


def format_date_full(date_str: str) -> str:
    """
    Convert date from DD-MM-YYYY to readable format

    Args:
        date_str: Date string in DD-MM-YYYY format

    Returns:
        Date string in readable format (e.g., "03 March 2025")

    Example:
        >>> format_date_full("03-03-2025")
        "03 March 2025"
    """
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime("%d %B %Y")
    except (ValueError, AttributeError):
        return date_str


def format_currency(amount: float, decimals: int = 2) -> str:
    """
    Format amount as Indian currency

    Args:
        amount: Amount to format
        decimals: Number of decimal places (default: 2)

    Returns:
        Formatted currency string with ₹ symbol

    Example:
        >>> format_currency(1234.56)
        "₹1,234.56"
    """
    return f"₹{amount:,.{decimals}f}"


def format_percentage(
    value: float, decimals: int = 2, include_sign: bool = False
) -> str:
    """
    Format value as percentage

    Args:
        value: Value to format
        decimals: Number of decimal places (default: 2)
        include_sign: Whether to include + for positive values

    Returns:
        Formatted percentage string

    Example:
        >>> format_percentage(12.345)
        "12.35%"
        >>> format_percentage(12.345, include_sign=True)
        "+12.35%"
    """
    sign = "+" if include_sign and value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values

    Args:
        old_value: Original value
        new_value: New value

    Returns:
        Percentage change (positive for increase, negative for decrease)

    Example:
        >>> calculate_percentage_change(100, 110)
        10.0
        >>> calculate_percentage_change(100, 90)
        -10.0
    """
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / old_value) * 100


def calculate_dip_percentage(peak_value: float, current_value: float) -> float:
    """
    Calculate dip percentage from peak

    Args:
        peak_value: Peak/highest value
        current_value: Current value

    Returns:
        Dip percentage (always positive or zero)

    Example:
        >>> calculate_dip_percentage(100, 90)
        10.0
    """
    if peak_value == 0:
        return 0.0
    dip = ((peak_value - current_value) / peak_value) * 100
    return max(0.0, dip)  # Ensure non-negative


def sort_nav_data_ascending(nav_data: List[Dict]) -> List[Dict]:
    """
    Sort NAV data by date in ascending order (oldest first)

    Args:
        nav_data: List of NAV entries with 'date' key

    Returns:
        Sorted list (oldest to newest)
    """
    return sorted(nav_data, key=lambda x: x["date"])


def sort_nav_data_descending(nav_data: List[Dict]) -> List[Dict]:
    """
    Sort NAV data by date in descending order (newest first)

    Args:
        nav_data: List of NAV entries with 'date' key

    Returns:
        Sorted list (newest to oldest)
    """
    return sorted(nav_data, key=lambda x: x["date"], reverse=True)


def get_latest_nav(nav_data: List[Dict]) -> Dict:
    """
    Get the most recent NAV entry from sorted or unsorted data

    Args:
        nav_data: List of NAV entries

    Returns:
        Most recent NAV entry

    Raises:
        ValueError: If nav_data is empty
    """
    if not nav_data:
        raise ValueError("NAV data is empty")

    return max(nav_data, key=lambda x: x["date"])


def get_oldest_nav(nav_data: List[Dict]) -> Dict:
    """
    Get the oldest NAV entry from sorted or unsorted data

    Args:
        nav_data: List of NAV entries

    Returns:
        Oldest NAV entry

    Raises:
        ValueError: If nav_data is empty
    """
    if not nav_data:
        raise ValueError("NAV data is empty")

    return min(nav_data, key=lambda x: x["date"])


def calculate_mean_nav(nav_data: List[Dict]) -> float:
    """
    Calculate mean NAV from data

    Args:
        nav_data: List of NAV entries

    Returns:
        Mean NAV value

    Raises:
        ValueError: If nav_data is empty
    """
    if not nav_data:
        raise ValueError("NAV data is empty")

    return sum(entry["nav"] for entry in nav_data) / len(nav_data)


def find_peak_nav(nav_data: List[Dict]) -> Dict:
    """
    Find entry with highest NAV

    Args:
        nav_data: List of NAV entries

    Returns:
        NAV entry with highest value

    Raises:
        ValueError: If nav_data is empty
    """
    if not nav_data:
        raise ValueError("NAV data is empty")

    return max(nav_data, key=lambda x: x["nav"])


def find_bottom_nav(nav_data: List[Dict]) -> Dict:
    """
    Find entry with lowest NAV

    Args:
        nav_data: List of NAV entries

    Returns:
        NAV entry with lowest value

    Raises:
        ValueError: If nav_data is empty
    """
    if not nav_data:
        raise ValueError("NAV data is empty")

    return min(nav_data, key=lambda x: x["nav"])


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating (default: "...")

    Returns:
        Truncated text

    Example:
        >>> truncate_text("This is a long text", 10)
        "This is..."
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def safe_round(value: float, decimals: int = 2) -> float:
    """
    Safely round a value, handling None and invalid inputs

    Args:
        value: Value to round
        decimals: Number of decimal places

    Returns:
        Rounded value or 0.0 if invalid
    """
    try:
        return round(float(value), decimals)
    except (TypeError, ValueError):
        return 0.0


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max

    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        Clamped value

    Example:
        >>> clamp(15, 0, 10)
        10
        >>> clamp(-5, 0, 10)
        0
    """
    return max(min_value, min(value, max_value))
