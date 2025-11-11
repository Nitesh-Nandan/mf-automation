import csv
import os
from pathlib import Path


def get_mf_funds():
    """
    Load all mutual fund data from mf_funds.csv into memory.
    Returns a list of dictionaries, where each dictionary represents a fund.
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    csv_path = script_dir / "mf_funds.csv"
    
    funds = []
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        # DictReader automatically skips the header and uses it as keys
        for row in csv_reader:
            funds.append(row)
    
    return funds


if __name__ == "__main__":
    # Example usage with dictionary format (recommended)
    print("Loading funds as dictionaries:")
    funds = get_mf_funds()
    for fund in funds:
        print(fund)
    
    print(f"\nTotal funds loaded: {len(funds)}")
    