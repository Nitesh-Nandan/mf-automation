"""
Batch Stock Analysis from Google Sheets
Reads stocks from Google Sheet and runs Technical Analysis on each
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sheet.google_sheet import SpreadSheet
from stocks.TechnicalAnalysis import TechnicalAnalysis


def analyze_from_sheet():
    """Read stocks from Google Sheet and analyze each one"""

    # Initialize Google Sheets connection
    sheet_url = "https://docs.google.com/spreadsheets/d/1uch8IQq3jJ_3QcYcm2LzPzYjb4zfVjX_ckoqjstVb0E"
    google_sheets = SpreadSheet(sheetUrl=sheet_url)

    # Get worksheet data
    print("📊 Reading stocks from Google Sheet (Emerging worksheet)...\n")
    worksheet = google_sheets.get_worksheet("Emerging")
    stocks_data = worksheet.get_all_records()

    if not stocks_data:
        print("❌ No stocks found in the sheet")
        return

    print(f"Found {len(stocks_data)} stocks to analyze\n")
    print("=" * 80)

    # Analyze each stock
    results = []
    for idx, stock in enumerate(stocks_data, 1):
        name = stock.get("name", "").strip()
        symbol = stock.get("symbol", "").strip()
        instrument_key = stock.get("instrument_key", "").strip()

        # Skip empty rows
        if not name or not symbol or not instrument_key:
            continue

        print(f"\n[{idx}/{len(stocks_data)}] Analyzing {symbol}...")
        print("-" * 80)

        try:
            # Run analysis
            analyzer = TechnicalAnalysis(
                stock_name=name, stock_symbol=symbol, instrument_key=instrument_key
            )

            result = analyzer.analyze()

            if result:
                results.append(result)

                # Print result
                print(f"{result['stock_name']} ({result['stock_symbol']})")
                print(
                    f"Price: ₹{result['current_price']:.2f}  |  RSI: {result['rsi']:.1f}  |  100 DMA: ₹{result['dma_100']:.2f}"
                )
                print(
                    f"Peak (90d): ₹{result['peak_90d']['price']:.2f}  |  Change: {result['change_from_peak_pct']:.2f}%"
                )
                print(
                    f"\n🎯 Score: {result['final_score']:.0f}/100  |  {result['recommendation']}  ({result['position_multiplier']}x)"
                )
                print(
                    f"Factors: Dip:{result['scores']['dip_depth']['score']:.0f} | Hist:{result['scores']['historical_context']['score']:.0f} | Mean:{result['scores']['mean_reversion']['score']:.0f} | Vol:{result['scores']['volatility']['score']:.0f} | Rec:{result['scores']['recovery_speed']['score']:.0f} | Tech:{result['scores']['technicals']['score']:.0f}"
                )
            else:
                print(f"❌ Analysis failed for {symbol}")

        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")

    # Summary
    print("\n" + "=" * 80)
    print(f"\n📋 ANALYSIS SUMMARY ({len(results)} stocks analyzed)")
    print("=" * 80)

    if results:
        # Sort by score
        results.sort(key=lambda x: x["final_score"], reverse=True)

        print(
            f"\n{'Rank':<6} {'Symbol':<12} {'Score':<8} {'Recommendation':<15} {'Price':<10} {'Change%':<10}"
        )
        print("-" * 80)

        for rank, r in enumerate(results, 1):
            print(
                f"{rank:<6} {r['stock_symbol']:<12} {r['final_score']:<8.0f} {r['recommendation']:<15} ₹{r['current_price']:<9.2f} {r['change_from_peak_pct']:<10.2f}"
            )

        # Top opportunities
        print("\n🎯 TOP OPPORTUNITIES (Score >= 60):")
        print("-" * 80)
        top_picks = [r for r in results if r["final_score"] >= 60]

        if top_picks:
            for r in top_picks:
                print(
                    f"  • {r['stock_symbol']:<12} Score: {r['final_score']:.0f}  |  {r['recommendation']}  |  ₹{r['current_price']:.2f}  |  {r['change_from_peak_pct']:.2f}%"
                )
        else:
            print("  No stocks meet the criteria (score >= 60)")

        # Stats
        avg_score = sum(r["final_score"] for r in results) / len(results)
        print(f"\n📊 Average Score: {avg_score:.1f}/100")
        print(
            f"📊 Stocks with BUY signal (75+): {len([r for r in results if r['final_score'] >= 75])}"
        )
        print(
            f"📊 Stocks with ACCUMULATE signal (60+): {len([r for r in results if r['final_score'] >= 60])}"
        )

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    analyze_from_sheet()
