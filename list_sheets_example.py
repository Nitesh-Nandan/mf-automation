#!/usr/bin/env python3
"""
Example script to list all sheets in a Google Spreadsheet
"""

from src.sheet.sheet_lister import list_all_sheets, extract_spreadsheet_id


def main():
    # Your Google Sheet URL
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1mOH2kkroxkS4H_rmfPO9hrdQkAvsp-z5EmRL0I7t1Ig/edit?gid=1583503000#gid=1583503000"
    
    print("🔍 Listing all sheets from Google Spreadsheet...")
    print(f"URL: {SHEET_URL}\n")
    
    # Extract and display spreadsheet ID
    spreadsheet_id = extract_spreadsheet_id(SHEET_URL)
    print(f"Spreadsheet ID: {spreadsheet_id}\n")
    
    # List all sheets with verbose output
    sheets = list_all_sheets(SHEET_URL, verbose=True)
    
    # If successful, show what you can do with the data
    if sheets:
        print("\n" + "="*70)
        print("📝 Programmatic Access Example:")
        print("="*70)
        print("\nYou can now access the sheets data like this:\n")
        
        for sheet in sheets:
            print(f"Sheet: {sheet['name']}")
            print(f"  - ID: {sheet['id']}")
            print(f"  - CSV URL: https://docs.google.com/spreadsheets/d/{sheet['spreadsheet_id']}/export?format=csv&gid={sheet['id']}")
        
        print("\n💡 To read data from a specific sheet:")
        print(f"   from src.sheet.sheet_lister import get_sheet_data_as_csv")
        print(f"   data = get_sheet_data_as_csv('{spreadsheet_id}', '{sheets[0]['id']}')")
        print(f"   # data is now a list of dictionaries")
        print(f"\n   # Or with pandas:")
        print(f"   import pandas as pd")
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheets[0]['id']}"
        print(f"   df = pd.read_csv('{csv_url}')")
    else:
        print("\n⚠️  Could not retrieve sheets.")
        print("\n📋 To make your Google Sheet publicly accessible:")
        print("   1. Open your Google Sheet")
        print("   2. Click the 'Share' button (top right)")
        print("   3. Click 'Change to anyone with the link'")
        print("   4. Make sure it's set to 'Viewer' (not 'Editor')")
        print("   5. Click 'Done'")
        print("\n   After these steps, run this script again!")


if __name__ == "__main__":
    main()

