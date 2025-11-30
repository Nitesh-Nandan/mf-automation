"""
Stock Analysis to Google Sheets
For each input worksheet, creates a separate output worksheet with analysis results
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sheet.google_sheet import SpreadSheet
from stocks.TechnicalAnalysis import TechnicalAnalysis


def read_and_analyze_sheet(google_sheets, sheet_name):
    """
    Read stocks from worksheet and analyze them

    Args:
        google_sheets: SpreadSheet instance
        sheet_name: Name of worksheet to read

    Returns:
        List of analysis results (sorted by score)
    """
    worksheet = google_sheets.get_worksheet(sheet_name)
    stocks_data = worksheet.get_all_records()

    # Filter valid stocks
    valid_stocks = [
        s
        for s in stocks_data
        if s.get("name", "").strip()
        and s.get("symbol", "").strip()
        and s.get("instrument_key", "").strip()
    ]

    print(f"Found {len(valid_stocks)} stocks in {sheet_name}\n")

    # Analyze each stock
    results = []
    for idx, stock in enumerate(valid_stocks, 1):
        symbol = stock["symbol"].strip()
        print(f"[{idx}/{len(valid_stocks)}] {symbol}...", end=" ")

        try:
            analyzer = TechnicalAnalysis(
                stock_name=stock["name"].strip(),
                stock_symbol=symbol,
                instrument_key=stock["instrument_key"].strip(),
            )

            result = analyzer.analyze()

            if result:
                results.append(result)
                print(f"✓ {result['final_score']:.0f}")
            else:
                print("✗")

        except Exception as e:
            print(f"✗ {e}")

    # Sort by score (descending)
    results.sort(key=lambda x: x["final_score"], reverse=True)

    return results


def write_results_to_sheet(google_sheets, sheet_name, results):
    """
    Write analysis results to new output worksheet

    Args:
        google_sheets: SpreadSheet instance
        sheet_name: Source worksheet name (for output name)
        results: List of analysis results

    Returns:
        Name of created worksheet
    """
    # Generate output worksheet name: {sheet_name}-Output
    output_name = f"{sheet_name}-Output"

    # Prepare headers
    headers = [
        "Date Time",
        "Symbol",
        "Name",
        "Price",
        "Change%",
        "RSI",
        "100DMA",
        "SCORE",
        "Recommendation",
        "Position",
        "Dip",
        "Hist",
        "Mean",
        "Vol",
        "Rec",
        "Tech",
        "Peak",
        "Peak Date",
        "Low",
        "Low Date",
        "Timestamp",
    ]

    # Prepare data rows
    current_datetime = datetime.now().strftime("%d %b %Y, %I:%M %p")
    rows = [headers]

    for r in results:
        row = [
            current_datetime,
            r["stock_symbol"],
            r["stock_name"],
            f"{r['current_price']:.2f}",
            f"{r['change_from_peak_pct']:.2f}",
            f"{r['rsi']:.2f}",
            f"{r['dma_100']:.2f}",
            r["final_score"],
            r["recommendation"],
            r["position_multiplier"],
            r["scores"]["dip_depth"]["score"],
            r["scores"]["historical_context"]["score"],
            r["scores"]["mean_reversion"]["score"],
            r["scores"]["volatility"]["score"],
            r["scores"]["recovery_speed"]["score"],
            r["scores"]["technicals"]["score"],
            f"{r['peak_90d']['price']:.2f}",
            r["peak_90d"]["date"],
            f"{r['low_90d']['price']:.2f}",
            r["low_90d"]["date"],
            r["analysis_date"],
        ]
        rows.append(row)

    # Check if worksheet already exists, if so clear it, otherwise create new one
    try:
        output_sheet = google_sheets.spreadsheet.worksheet(output_name)
        # Clear existing data
        output_sheet.clear()
        print(f"   Cleared existing worksheet: {output_name}")
    except:
        # Worksheet doesn't exist, create new one
        output_sheet = google_sheets.spreadsheet.add_worksheet(
            title=output_name, rows=len(rows) + 10, cols=len(headers)
        )
        print(f"   Created new worksheet: {output_name}")

    # Update with new data
    output_sheet.update(range_name="A1", values=rows)

    return output_name


def analyze_and_update_sheet(
    sheet_names: list[str],
    sheet_url: str = "https://docs.google.com/spreadsheets/d/1uch8IQq3jJ_3QcYcm2LzPzYjb4zfVjX_ckoqjstVb0E",
):
    """
    Main function: Analyze stocks from worksheets and create output worksheets

    Args:
        sheet_names: List of worksheet names (e.g., ["Emerging", "Bluechip"])
        sheet_url: Google Sheets URL

    Example:
        analyze_and_update_sheet(["Emerging", "Bluechip"])
        Creates: Emerging-Output-30Nov24-1159, Bluechip-Output-30Nov24-1200
    """
    print(f"📊 Connecting to Google Sheet...\n")
    google_sheets = SpreadSheet(sheetUrl=sheet_url)

    for sheet_name in sheet_names:
        print(f"{'='*80}")
        print(f"Processing: {sheet_name}")
        print(f"{'='*80}\n")

        try:
            # Read and analyze
            results = read_and_analyze_sheet(google_sheets, sheet_name)

            if not results:
                print(f"\n⚠️  No results for {sheet_name}, skipping\n")
                continue

            # Write to output sheet
            print(f"\n📝 Creating output worksheet...")
            output_name = write_results_to_sheet(google_sheets, sheet_name, results)

            print(f"✅ Written {len(results)} results to {output_name}")

            # Quick stats
            avg_score = sum(r["final_score"] for r in results) / len(results)
            buy_count = len([r for r in results if r["final_score"] >= 75])
            acc_count = len([r for r in results if r["final_score"] >= 60])

            print(
                f"   Avg: {avg_score:.1f} | BUY: {buy_count} | ACCUMULATE: {acc_count}"
            )

            # Top 3
            print(f"   Top 3:")
            for i, r in enumerate(results[:3], 1):
                print(
                    f"      {i}. {r['stock_symbol']:<12} {r['final_score']:.0f} | {r['recommendation']}"
                )

            print()

        except Exception as e:
            print(f"❌ Error processing {sheet_name}: {e}\n")

    print(f"{'='*80}")
    print("✅ All worksheets processed!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Analyze stocks from Emerging worksheet
    analyze_and_update_sheet(["Emerging", "Monopoly"])

    # Or analyze multiple worksheets:
    # analyze_and_update_sheet(["Emerging", "Bluechip", "Current"])
