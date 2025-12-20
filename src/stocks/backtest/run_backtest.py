#!/usr/bin/env python3
"""
CLI Runner for Stock Backtest

Usage:
    # Single stock backtest
    python src/stocks/backtest/run_backtest.py --symbol ASIANPAINT --name "Asian Paints" --key "NSE_EQ|INE021A01026"

    # Batch backtest from CSV
    python src/stocks/backtest/run_backtest.py --csv src/stocks/stocks_watchlist.csv --mode conservative

    # Custom parameters
    python src/stocks/backtest/run_backtest.py --csv stocks.csv --days 365 --capital 200000 --investment 20000
"""

import argparse
import csv
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from stocks.backtest.backtest_stock_strategy import (
    run_backtest_for_stock,
    save_backtest_results,
    RECOMMENDATION_THRESHOLDS,
)


def run_batch_backtest(
    csv_path: str,
    backtest_days: int = 730,
    initial_capital: float = 100000,
    investment_per_signal: float = 10000,
    mode: str = "conservative",
    output_dir: str = ".",
    delay: float = 1.0,
):
    """
    Run backtest on multiple stocks from CSV

    Args:
        csv_path: Path to CSV file with columns: name, symbol, instrument_key
        backtest_days: Number of days to backtest
        initial_capital: Starting capital per stock
        investment_per_signal: Amount per buy signal
        mode: Risk mode
        output_dir: Directory to save results
        delay: Delay between API calls (seconds) to avoid rate limits
    """
    print(f"\n{'='*80}")
    print(f"🔬 BACKTESTING STOCK STRATEGY - {mode.upper()} MODE")
    print(f"{'='*80}")
    print(f"Period: Last {backtest_days} days (~{backtest_days//365} years)")
    print(f"Initial Capital: ₹{initial_capital:,.0f} per stock")
    print(f"Investment per Signal: ₹{investment_per_signal:,.0f}")
    print(f"Buy Threshold: {RECOMMENDATION_THRESHOLDS[mode]} points")
    print(f"{'='*80}\n")

    # Load stocks from CSV
    try:
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            stocks = list(reader)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []

    if not stocks:
        print(f"❌ No stocks found in {csv_path}")
        return []

    print(f"Loaded {len(stocks)} stocks from {csv_path}\n")

    results = []

    for i, stock in enumerate(stocks, 1):
        # Validate required fields
        if not all(k in stock for k in ["name", "symbol", "instrument_key"]):
            print(
                f"⚠️  Skipping row {i} - Missing required fields (name, symbol, instrument_key)"
            )
            continue

        stock_name = stock["name"].strip()
        stock_symbol = stock["symbol"].strip()
        instrument_key = stock["instrument_key"].strip()

        if not stock_name or not stock_symbol or not instrument_key:
            print(f"⚠️  Skipping {stock_symbol or 'unknown'} - Empty fields")
            continue

        print(f"[{i}/{len(stocks)}] Backtesting {stock_symbol} ({stock_name})...")

        try:
            result = run_backtest_for_stock(
                stock_name=stock_name,
                stock_symbol=stock_symbol,
                instrument_key=instrument_key,
                backtest_days=backtest_days,
                initial_capital=initial_capital,
                investment_per_signal=investment_per_signal,
                mode=mode,
            )

            if result.get("error"):
                print(f"  ❌ Error: {result['error']}")
            else:
                results.append(result)
                print(
                    f"  ✅ Completed | Signals: {result['num_transactions']} | "
                    f"Return: {result['strategy_return_pct']:+.2f}% | "
                    f"vs Baseline: {result['outperformance']:+.2f}%"
                )

        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")

        # Rate limiting delay
        if i < len(stocks):
            time.sleep(delay)

    print(f"\n{'='*80}")
    print(f"✅ Backtest Complete! {len(results)}/{len(stocks)} stocks successful")
    print(f"{'='*80}\n")

    # Save results
    if results:
        save_backtest_results(results, mode, output_dir)

    return results


def run_single_backtest(
    stock_name: str,
    stock_symbol: str,
    instrument_key: str,
    backtest_days: int = 730,
    initial_capital: float = 100000,
    investment_per_signal: float = 10000,
    mode: str = "conservative",
    output_dir: str = ".",
):
    """
    Run backtest on a single stock
    """
    print(f"\n{'='*80}")
    print(f"🔬 BACKTESTING {stock_symbol} - {mode.upper()} MODE")
    print(f"{'='*80}")
    print(f"Period: Last {backtest_days} days (~{backtest_days//365} years)")
    print(f"Initial Capital: ₹{initial_capital:,.0f}")
    print(f"Investment per Signal: ₹{investment_per_signal:,.0f}")
    print(f"Buy Threshold: {RECOMMENDATION_THRESHOLDS[mode]} points")
    print(f"{'='*80}\n")

    try:
        result = run_backtest_for_stock(
            stock_name=stock_name,
            stock_symbol=stock_symbol,
            instrument_key=instrument_key,
            backtest_days=backtest_days,
            initial_capital=initial_capital,
            investment_per_signal=investment_per_signal,
            mode=mode,
        )

        if result.get("error"):
            print(f"\n❌ Error: {result['error']}")
            return [result]

        print(f"\n{'='*80}")
        print(f"✅ RESULTS")
        print(f"{'='*80}")
        print(f"Signals: {result['num_transactions']}")
        print(f"Total Invested: ₹{result['total_invested']:,.0f}")
        print(f"Strategy Return: {result['strategy_return_pct']:+.2f}%")
        print(f"Baseline Return: {result['baseline_return_pct']:+.2f}%")
        print(f"Outperformance: {result['outperformance']:+.2f}%")
        print(f"Win Rate: {result['win_rate']:.1f}%")
        print(f"{'='*80}\n")

        # Save results
        save_backtest_results([result], mode, output_dir)

        return [result]

    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Backtest stock technical analysis dip buying strategy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single stock backtest
  python run_backtest.py --symbol ASIANPAINT --name "Asian Paints" --key "NSE_EQ|INE021A01026"
  
  # Batch backtest from CSV
  python run_backtest.py --csv ../stocks_watchlist.csv --mode conservative
  
  # Custom parameters (1 year, aggressive mode)
  python run_backtest.py --csv stocks.csv --days 365 --mode aggressive
  
  # Higher capital allocation
  python run_backtest.py --csv stocks.csv --capital 500000 --investment 50000
        """,
    )

    # Input source (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--csv",
        help="Path to CSV file with stocks (columns: name, symbol, instrument_key)",
    )
    input_group.add_argument(
        "--symbol", help="Stock symbol (for single stock backtest)"
    )

    # Single stock parameters
    parser.add_argument("--name", help="Stock name (required with --symbol)")
    parser.add_argument("--key", help="Instrument key (required with --symbol)")

    # Backtest parameters
    parser.add_argument(
        "--mode",
        choices=["ultra_conservative", "conservative", "moderate", "aggressive"],
        default="conservative",
        help="Risk mode / buy threshold (default: conservative = 75 pts)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=730,
        help="Number of days to backtest (default: 730 = 2 years)",
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=100000,
        help="Initial capital per stock (default: 100000)",
    )
    parser.add_argument(
        "--investment",
        type=float,
        default=10000,
        help="Amount to invest per buy signal (default: 10000)",
    )
    parser.add_argument(
        "--output",
        default=".",
        help="Output directory for results (default: current directory)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (default: 1.0)",
    )

    args = parser.parse_args()

    # Validate single stock parameters
    if args.symbol and (not args.name or not args.key):
        parser.error("--symbol requires --name and --key")

    # Run appropriate backtest
    if args.csv:
        run_batch_backtest(
            csv_path=args.csv,
            backtest_days=args.days,
            initial_capital=args.capital,
            investment_per_signal=args.investment,
            mode=args.mode,
            output_dir=args.output,
            delay=args.delay,
        )
    else:
        run_single_backtest(
            stock_name=args.name,
            stock_symbol=args.symbol,
            instrument_key=args.key,
            backtest_days=args.days,
            initial_capital=args.capital,
            investment_per_signal=args.investment,
            mode=args.mode,
            output_dir=args.output,
        )


if __name__ == "__main__":
    main()







