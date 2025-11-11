"""
Fund Loader Module

Loads mutual fund portfolio from CSV file.
"""

import csv
from pathlib import Path
from typing import List

from .constants import FUND_CSV_FILENAME
from .exceptions import FundNotFoundError
from .types import FundInfo


def get_mf_funds() -> List[FundInfo]:
    """
    Load all mutual fund data from mf_funds.csv into memory.

    Returns:
        List of fund information dictionaries

    Raises:
        FileNotFoundError: If CSV file doesn't exist

    Example:
        >>> funds = get_mf_funds()
        >>> print(funds[0]['fund_name'])
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    csv_path = script_dir / FUND_CSV_FILENAME

    if not csv_path.exists():
        raise FileNotFoundError(f"Fund CSV file not found: {csv_path}")

    funds: List[FundInfo] = []

    with open(csv_path, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            funds.append(row)  # type: ignore

    return funds


def get_fund_by_code(code: str) -> FundInfo:
    """
    Get a specific fund by its API code

    Args:
        code: Fund API code

    Returns:
        Fund information dictionary

    Raises:
        FundNotFoundError: If fund with given code is not found
    """
    funds = get_mf_funds()

    for fund in funds:
        if fund["code"] == code:
            return fund

    raise FundNotFoundError(code)


def get_fund_by_name(name: str, exact: bool = False) -> FundInfo:
    """
    Get a specific fund by its name

    Args:
        name: Fund name or partial name
        exact: Whether to match exact name (default: False for partial matching)

    Returns:
        Fund information dictionary

    Raises:
        FundNotFoundError: If fund with given name is not found
    """
    funds = get_mf_funds()

    name_lower = name.lower()

    for fund in funds:
        fund_name_lower = fund["fund_name"].lower()

        if exact:
            if fund_name_lower == name_lower:
                return fund
        else:
            if name_lower in fund_name_lower:
                return fund

    raise FundNotFoundError(name)
