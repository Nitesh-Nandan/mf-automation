"""
Standalone runner script for Stock Technical Analysis
Run this file directly: python src/stocks/run_analysis.py
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from stocks.TechnicalAnalysis import TechnicalAnalysis
from stocks.historical_data import get_ltp


def main():
    """Run example stock analysis"""

    print("\n📊 Stock Technical Analysis\n")

    # Example: Analyze Asian Paints
    analyzer = TechnicalAnalysis(
        stock_name="IRCTC Limited",
        stock_symbol="IRCTC",
        instrument_key="NSE_EQ|INE335Y01020",
    )

    print(get_ltp(analyzer.instrument_key))
    print("--------------------------------")

    result = analyzer.analyze()

    if result:
        print(f"\n{result['stock_name']} ({result['stock_symbol']})")
        print(f"{'─'*50}")
        print(
            f"Price: ₹{result['current_price']:.2f}  |  RSI: {result['rsi']:.1f}  |  100 DMA: ₹{result['dma_100']:.2f}"
        )
        print(
            f"Peak (90d): ₹{result['peak_90d']['price']:.2f}  |  Change: {result['change_from_peak_pct']:.2f}%"
        )
        print(
            f"\n🎯 Score: {result['final_score']:.0f}/100  |  {result['recommendation']}  ({result['position_multiplier']}x)"
        )
        print(f"{'─'*50}")
        print(
            f"\nFactors: Dip:{result['scores']['dip_depth']['score']:.0f} | Hist:{result['scores']['historical_context']['score']:.0f} | Mean:{result['scores']['mean_reversion']['score']:.0f} | Vol:{result['scores']['volatility']['score']:.0f} | Rec:{result['scores']['recovery_speed']['score']:.0f} | Tech:{result['scores']['technicals']['score']:.0f}"
        )
        print()
    else:
        print("\n❌ Analysis failed\n")


if __name__ == "__main__":
    main()
