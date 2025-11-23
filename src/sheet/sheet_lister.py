#!/usr/bin/env python3
"""
Google Sheets Tab Lister
Lists all sheets/tabs in a Google Spreadsheet using Google Sheets API
"""

import re
import requests
from typing import List, Dict, Optional


def extract_spreadsheet_id(url: str) -> str:
    """
    Extract spreadsheet ID from Google Sheets URL
    
    Args:
        url: Full Google Sheets URL or just the ID
        
    Returns:
        Spreadsheet ID string
        
    Example:
        >>> extract_spreadsheet_id("https://docs.google.com/spreadsheets/d/ABC123/edit")
        'ABC123'
    """
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    return url  # Assume it's already just the ID


def extract_sheet_id(url: str) -> Optional[str]:
    """
    Extract sheet ID (gid) from Google Sheets URL
    
    Args:
        url: Full Google Sheets URL
        
    Returns:
        Sheet ID (gid) string or None if not found
        
    Example:
        >>> extract_sheet_id("https://docs.google.com/spreadsheets/d/ABC123/edit#gid=1583503000")
        '1583503000'
    """
    match = re.search(r'[#&]gid=([0-9]+)', url)
    if match:
        return match.group(1)
    return None  # Default sheet is gid=0


def get_sheet_data_as_csv(spreadsheet_id: str, sheet_id: str = "0") -> List[Dict]:
    """
    Get data from a specific sheet as CSV
    
    Args:
        spreadsheet_id: The spreadsheet ID
        sheet_id: The sheet ID (gid), default is "0" for first sheet
        
    Returns:
        List of dictionaries with row data
        
    Example:
        >>> data = get_sheet_data_as_csv("ABC123", "0")
        >>> print(data)
    """
    import csv
    from io import StringIO
    sheet_id = '794212619'
    
    csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"
    
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        
        # Parse CSV
        csv_data = csv.DictReader(StringIO(response.text))
        return list(csv_data)
        
    except Exception as e:
        print(f"❌ Error reading sheet data: {e}")
        return []


def get_sheet_data_from_url(sheet_url: str) -> List[Dict]:
    """
    Get data from a Google Sheet using its full URL
    Automatically extracts spreadsheet ID and sheet ID (gid) from the URL
    
    Args:
        sheet_url: Full Google Sheets URL
        
    Returns:
        List of dictionaries with row data
        
    Example:
        >>> url = "https://docs.google.com/spreadsheets/d/ABC123/edit#gid=0"
        >>> data = get_sheet_data_from_url(url)
        >>> print(data)
    """
    spreadsheet_id = extract_spreadsheet_id(sheet_url)
    sheet_id = extract_sheet_id(sheet_url) or "0"
    
    print(f"📊 Reading sheet from:")
    print(f"   Spreadsheet ID: {spreadsheet_id}")
    print(f"   Sheet ID (gid): {sheet_id}")
    
    data = get_sheet_data_as_csv(spreadsheet_id, sheet_id)
    
    if data:
        print(f"✅ Loaded {len(data)} rows")
    else:
        print("⚠️  No data found or sheet is empty")
    
    return data




def main():
    """
    Main function to demonstrate usage
    """
    # Your Google Sheet URL
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1mOH2kkroxkS4H_rmfPO9hrdQkAvsp-z5EmRL0I7t1Ig/edit#gid=1583503000"
    
    print("=" * 70)
    print("Google Sheets Data Reader")
    print("=" * 70)
    print(f"\n🔗 Sheet URL: {SHEET_URL}\n")
    
    # Read data directly via CSV export
    print("📊 Reading data from sheet...")
    data = get_sheet_data_from_url(SHEET_URL)
    
    if data:
        print("\n✅ Data preview (first 5 rows):")
        for i, row in enumerate(data[:5], 1):
            print(f"   Row {i}: {row}")
    
    print("\n💡 To use this in your code:")
    print("   from src.sheet import get_sheet_data_from_url")
    print(f"   data = get_sheet_data_from_url('{SHEET_URL}')")


if __name__ == "__main__":
    main()

