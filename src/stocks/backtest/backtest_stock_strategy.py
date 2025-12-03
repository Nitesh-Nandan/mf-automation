"""
Comprehensive Backtest for Stock Technical Analysis Dip Buying Strategy

This backtest simulates the dip-buying strategy over historical periods:
- Uses actual scoring algorithm from TechnicalScore.py
- No future peeking (only uses data available at each decision point)
- Handles missing data gracefully
- Generates detailed performance reports with win rate, recovery times, etc.
"""

import json
import statistics
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from stocks.historical_data import get_historical_data, IntervalUnit
from stocks.models import OHLCVData
from stocks.TechnicalScore import (
    score_dip_depth,
    score_historical_context,
    score_mean_reversion,
    score_volatility,
    score_recovery_speed,
    score_technicals,
    get_recommendation,
)


# Recommendation thresholds
RECOMMENDATION_THRESHOLDS = {
    "ultra_conservative": 85,  # STRONG BUY only
    "conservative": 75,  # BUY or better
    "moderate": 60,  # ACCUMULATE or better
    "aggressive": 50,  # NIBBLE or better
}


class StockBacktestEngine:
    """
    Backtest engine for stock technical analysis dip buying strategy

    Simulates historical performance by:
    1. Walking through time week-by-week
    2. Calculating scores using only past data (no future peeking)
    3. Making buy decisions based on score thresholds
    4. Tracking portfolio value over time
    5. Comparing against buy-and-hold baseline
    """

    def __init__(
        self,
        stock_name: str,
        stock_symbol: str,
        instrument_key: str,
        backtest_days: int = 730,  # 2 years
        initial_capital: float = 100000,
        investment_per_signal: float = 10000,
        mode: str = "conservative",
    ):
        """
        Initialize backtest engine

        Args:
            stock_name: Name of the stock
            stock_symbol: NSE symbol
            instrument_key: Upstox instrument key
            backtest_days: Number of days to backtest
            initial_capital: Starting capital
            investment_per_signal: Amount to invest per buy signal
            mode: Risk mode (ultra_conservative, conservative, moderate, aggressive)
        """
        self.stock_name = stock_name
        self.stock_symbol = stock_symbol
        self.instrument_key = instrument_key
        self.backtest_days = backtest_days
        self.initial_capital = initial_capital
        self.investment_per_signal = investment_per_signal
        self.mode = mode
        self.threshold = RECOMMENDATION_THRESHOLDS.get(mode, 75)

        # Portfolio tracking
        self.capital = initial_capital
        self.shares = 0.0
        self.transactions = []
        self.daily_portfolio_values = []

        # Historical data
        self.price_data: List[OHLCVData] = []
        self.data_fetch_error = None

    def fetch_historical_data(self, lookback_days: int = 1095) -> bool:
        """
        Fetch historical price data for backtesting

        Args:
            lookback_days: Total days to fetch (backtest period + analysis buffer)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Calculate dates
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - timedelta(days=lookback_days)).strftime(
                "%Y-%m-%d"
            )

            print(f"  Fetching {lookback_days} days of data...")

            # Fetch historical data
            hist_response = get_historical_data(
                self.instrument_key,
                to_date,
                from_date,
                unit=IntervalUnit.DAYS,
                interval="1",
            )

            if not hist_response or not hist_response.get("data", {}).get("candles"):
                self.data_fetch_error = "No data returned from API"
                return False

            # Transform to OHLCVData format
            raw_candles = hist_response["data"]["candles"]
            self.price_data = []

            for candle in raw_candles:
                self.price_data.append(
                    {
                        "date": candle[0].split("T")[0],
                        "open": float(candle[1]),
                        "high": float(candle[2]),
                        "low": float(candle[3]),
                        "close": float(candle[4]),
                        "volume": int(candle[5]) if len(candle) > 5 else 0,
                    }
                )

            # Sort by date (oldest first)
            self.price_data.sort(key=lambda x: x["date"])

            print(f"  ✓ Fetched {len(self.price_data)} days of data")
            return len(self.price_data) >= 200  # Need at least 200 days

        except Exception as e:
            self.data_fetch_error = str(e)
            return False

    def _calculate_score_at_date(
        self, data_up_to_date: List[OHLCVData], current_price: float
    ) -> Tuple[float, Dict]:
        """
        Calculate technical score using only data available up to a specific date
        (No future peeking!)

        Args:
            data_up_to_date: Historical data up to evaluation date
            current_price: Price at evaluation date

        Returns:
            Tuple of (total_score, score_breakdown)
        """
        if len(data_up_to_date) < 100:
            return 0.0, {}

        # Get 90-day and 2-year windows
        data_90d = (
            data_up_to_date[-90:] if len(data_up_to_date) >= 90 else data_up_to_date
        )
        data_2yr = (
            data_up_to_date[-500:] if len(data_up_to_date) >= 500 else data_up_to_date
        )

        # Calculate indicators
        peak_90d = max(data_90d, key=lambda x: x["high"])
        low_90d = min(data_90d, key=lambda x: x["low"])

        peak_price = peak_90d["high"]
        change_from_peak_pct = ((current_price - peak_price) / peak_price) * 100
        current_dip = abs(change_from_peak_pct)

        # DMAs
        dma_50 = self._calculate_sma(data_up_to_date, 50)
        dma_100 = self._calculate_sma(data_up_to_date, 100)
        dma_200 = self._calculate_sma(data_up_to_date, 200)

        # RSI
        rsi = self._calculate_rsi(data_up_to_date, 14)

        # Volatility
        vol_90d = self._calculate_volatility(data_90d)
        vol_2yr = self._calculate_volatility(data_2yr)

        # Volume
        avg_vol_20d = self._calculate_avg_volume(data_up_to_date, 20)
        current_vol = data_up_to_date[-1]["volume"] if data_up_to_date else 0
        vol_ratio = current_vol / avg_vol_20d if avg_vol_20d > 0 else 1.0

        # Calculate all 6 factor scores
        # Factor 1: Dip Depth
        dip_depth_score = score_dip_depth(current_dip)

        # Factor 2: Historical Context
        max_hist_dip = self._calculate_max_historical_dip(data_up_to_date)
        historical_score = score_historical_context(current_dip, max_hist_dip)

        # Factor 3: Mean Reversion
        mean_rev_score = score_mean_reversion(current_price, dma_100)

        # Factor 4: Volatility
        volatility_score = score_volatility(vol_90d, vol_2yr)

        # Factor 5: Recovery Speed
        avg_recovery, count = self._calculate_recovery_speed(data_up_to_date)
        recovery_score = score_recovery_speed(avg_recovery, count)

        # Factor 6: Technicals
        dist_50 = abs((current_price - dma_50) / dma_50 * 100) if dma_50 > 0 else 100
        dist_100 = (
            abs((current_price - dma_100) / dma_100 * 100) if dma_100 > 0 else 100
        )
        technical_score = score_technicals(rsi, vol_ratio, dist_50, dist_100)

        # Total score
        total = sum(
            [
                dip_depth_score["score"],
                historical_score["score"],
                mean_rev_score["score"],
                volatility_score["score"],
                recovery_score["score"],
                technical_score["score"],
            ]
        )

        breakdown = {
            "dip_depth": dip_depth_score,
            "historical_context": historical_score,
            "mean_reversion": mean_rev_score,
            "volatility": volatility_score,
            "recovery_speed": recovery_score,
            "technicals": technical_score,
            "rsi": rsi,
            "dma_100": dma_100,
            "change_from_peak_pct": change_from_peak_pct,
        }

        return round(total, 2), breakdown

    def _calculate_sma(self, data: List[OHLCVData], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return 0.0
        closes = [d["close"] for d in data[-period:]]
        return sum(closes) / period

    def _calculate_rsi(self, data: List[OHLCVData], period: int = 14) -> float:
        """Calculate RSI"""
        if len(data) < period + 1:
            return 50.0

        closes = [d["close"] for d in data[-(period + 1) :]]
        gains, losses = [], []

        for i in range(1, len(closes)):
            change = closes[i] - closes[i - 1]
            gains.append(max(change, 0))
            losses.append(abs(min(change, 0)))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _calculate_avg_volume(self, data: List[OHLCVData], period: int) -> float:
        """Calculate average volume"""
        if len(data) < period:
            return 0.0
        volumes = [d["volume"] for d in data[-period:]]
        return sum(volumes) / period

    def _calculate_volatility(self, data: List[OHLCVData]) -> float:
        """Calculate annualized volatility"""
        if len(data) < 2:
            return 0.0

        returns = []
        for i in range(1, len(data)):
            ret = (data[i]["close"] - data[i - 1]["close"]) / data[i - 1]["close"]
            returns.append(ret)

        if not returns:
            return 0.0

        std_dev = statistics.stdev(returns)
        return std_dev * (252**0.5) * 100

    def _calculate_max_historical_dip(self, price_data: List[OHLCVData]) -> float:
        """Calculate maximum historical dip over available data"""
        max_dip = 0.0
        for i in range(90, len(price_data)):
            window = price_data[i - 90 : i]
            peak = max(window, key=lambda x: x["high"])["high"]
            current = price_data[i]["close"]
            dip = ((peak - current) / peak) * 100
            max_dip = max(max_dip, dip)
        return max_dip

    def _calculate_recovery_speed(
        self, price_data: List[OHLCVData]
    ) -> Tuple[float, int]:
        """Calculate average recovery speed from significant dips"""
        recoveries = []

        for i in range(90, len(price_data) - 20):
            window = price_data[i - 90 : i]
            peak = max(window, key=lambda x: x["high"])["high"]
            current = price_data[i]["close"]
            dip_pct = ((peak - current) / peak) * 100

            if dip_pct >= 8:  # Significant dip
                # Look for recovery (99% of peak)
                for j in range(i + 1, min(i + 91, len(price_data))):
                    if price_data[j]["close"] >= peak * 0.99:
                        recoveries.append(j - i)
                        break

        if not recoveries:
            return 60.0, 0  # Default moderate recovery

        return sum(recoveries) / len(recoveries), len(recoveries)

    def run_backtest(self, evaluation_interval: int = 7) -> Dict:
        """
        Run the backtest simulation

        Args:
            evaluation_interval: Days between evaluations (default: 7 = weekly)

        Returns:
            Dictionary with backtest results
        """
        if not self.price_data:
            if not self.fetch_historical_data():
                return {"error": f"Failed to fetch data: {self.data_fetch_error}"}

        # Define backtest period (last N days)
        all_dates = [d["date"] for d in self.price_data]
        backtest_start_idx = max(0, len(self.price_data) - self.backtest_days)

        if backtest_start_idx < 100:
            return {
                "error": "Insufficient data for backtest period (need 100+ days before start)"
            }

        # Baseline: buy-and-hold from start
        baseline_start_price = self.price_data[backtest_start_idx]["close"]
        baseline_shares = self.initial_capital / baseline_start_price

        # Run simulation - evaluate at weekly intervals
        evaluation_indices = list(
            range(backtest_start_idx, len(self.price_data), evaluation_interval)
        )

        print(f"  Evaluating {len(evaluation_indices)} time points...")

        for idx in evaluation_indices:
            if idx >= len(self.price_data):
                break

            current_date = self.price_data[idx]["date"]
            current_price = self.price_data[idx]["close"]

            # Calculate score using only data up to this point
            data_up_to_now = self.price_data[: idx + 1]
            score, breakdown = self._calculate_score_at_date(
                data_up_to_now, current_price
            )

            # Buy decision
            if score >= self.threshold and self.capital >= self.investment_per_signal:
                shares_to_buy = self.investment_per_signal / current_price
                self.shares += shares_to_buy
                self.capital -= self.investment_per_signal

                recommendation, multiplier = get_recommendation(score)

                self.transactions.append(
                    {
                        "date": current_date,
                        "price": current_price,
                        "shares": shares_to_buy,
                        "amount": self.investment_per_signal,
                        "score": score,
                        "recommendation": recommendation,
                        "breakdown": breakdown,
                    }
                )

        # Calculate final values
        final_price = self.price_data[-1]["close"]
        final_date = self.price_data[-1]["date"]

        strategy_value = (self.shares * final_price) + self.capital
        baseline_value = baseline_shares * final_price

        total_invested = sum(t["amount"] for t in self.transactions)
        avg_buy_price = total_invested / self.shares if self.shares > 0 else 0

        strategy_return_pct = (
            (strategy_value - self.initial_capital) / self.initial_capital
        ) * 100
        baseline_return_pct = (
            (baseline_value - self.initial_capital) / self.initial_capital
        ) * 100
        outperformance = strategy_return_pct - baseline_return_pct

        # Calculate per-transaction returns (for those that have time to mature)
        profitable_count = 0
        for txn in self.transactions:
            txn["current_value"] = txn["shares"] * final_price
            txn["return_pct"] = (
                (txn["current_value"] - txn["amount"]) / txn["amount"]
            ) * 100
            if txn["return_pct"] > 0:
                profitable_count += 1

        win_rate = (
            (profitable_count / len(self.transactions) * 100)
            if self.transactions
            else 0
        )

        return {
            "stock_name": self.stock_name,
            "stock_symbol": self.stock_symbol,
            "mode": self.mode,
            "threshold": self.threshold,
            "backtest_period_days": self.backtest_days,
            "backtest_start_date": self.price_data[backtest_start_idx]["date"],
            "backtest_end_date": final_date,
            "num_transactions": len(self.transactions),
            "total_invested": total_invested,
            "shares_accumulated": self.shares,
            "avg_buy_price": avg_buy_price,
            "final_price": final_price,
            "strategy_final_value": strategy_value,
            "remaining_capital": self.capital,
            "strategy_return_pct": round(strategy_return_pct, 2),
            "baseline_start_price": baseline_start_price,
            "baseline_shares": baseline_shares,
            "baseline_final_value": baseline_value,
            "baseline_return_pct": round(baseline_return_pct, 2),
            "outperformance": round(outperformance, 2),
            "win_rate": round(win_rate, 1),
            "transactions": self.transactions,
        }


def run_backtest_for_stock(
    stock_name: str,
    stock_symbol: str,
    instrument_key: str,
    backtest_days: int = 730,
    initial_capital: float = 100000,
    investment_per_signal: float = 10000,
    mode: str = "conservative",
) -> Dict:
    """
    Run backtest for a single stock

    Args:
        stock_name: Name of the stock
        stock_symbol: NSE symbol
        instrument_key: Upstox instrument key
        backtest_days: Number of days to backtest
        initial_capital: Starting capital
        investment_per_signal: Amount per buy signal
        mode: Risk mode

    Returns:
        Backtest results dictionary
    """
    engine = StockBacktestEngine(
        stock_name=stock_name,
        stock_symbol=stock_symbol,
        instrument_key=instrument_key,
        backtest_days=backtest_days,
        initial_capital=initial_capital,
        investment_per_signal=investment_per_signal,
        mode=mode,
    )

    return engine.run_backtest()


def generate_backtest_report(results: List[Dict], mode: str) -> str:
    """
    Generate human-readable backtest report

    Args:
        results: List of backtest results
        mode: Risk mode used

    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append(f"STOCK DIP BUYING STRATEGY - BACKTEST REPORT ({mode.upper()} MODE)")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Threshold: {RECOMMENDATION_THRESHOLDS.get(mode, 75)} points")
    report.append("")

    # Overall statistics
    successful = [r for r in results if not r.get("error")]

    if not successful:
        report.append("❌ No successful backtests")
        return "\n".join(report)

    total_transactions = sum(r["num_transactions"] for r in successful)
    avg_outperformance = statistics.mean([r["outperformance"] for r in successful])
    winning_stocks = len([r for r in successful if r["outperformance"] > 0])

    report.append("📊 OVERALL SUMMARY")
    report.append("-" * 80)
    report.append(f"Stocks Tested: {len(successful)}")
    report.append(f"Total Buy Signals: {total_transactions}")
    report.append(f"Avg Outperformance: {avg_outperformance:+.2f}%")
    report.append(
        f"Stocks Beating Baseline: {winning_stocks}/{len(successful)} ({winning_stocks/len(successful)*100:.1f}%)"
    )
    report.append("")

    # Individual stock results
    report.append("📈 INDIVIDUAL STOCK RESULTS")
    report.append("-" * 80)

    for r in sorted(successful, key=lambda x: x["outperformance"], reverse=True):
        report.append(f"\n{r['stock_symbol']} - {r['stock_name']}")
        report.append(
            f"  Period: {r['backtest_start_date']} to {r['backtest_end_date']} ({r['backtest_period_days']} days)"
        )
        report.append(f"  Signals: {r['num_transactions']}")
        report.append(f"  Total Invested: ₹{r['total_invested']:,.0f}")
        report.append(
            f"  Avg Buy Price: ₹{r['avg_buy_price']:.2f} | Final Price: ₹{r['final_price']:.2f}"
        )
        report.append(f"  Strategy Return: {r['strategy_return_pct']:+.2f}%")
        report.append(f"  Baseline Return: {r['baseline_return_pct']:+.2f}%")
        report.append(f"  Outperformance: {r['outperformance']:+.2f}%")
        report.append(f"  Win Rate: {r['win_rate']:.1f}%")

        if r["transactions"]:
            report.append(f"\n  Top 3 Buys:")
            top_txns = sorted(
                r["transactions"], key=lambda x: x.get("return_pct", 0), reverse=True
            )[:3]
            for i, txn in enumerate(top_txns, 1):
                report.append(
                    f"    {i}. {txn['date']} | ₹{txn['price']:.2f} | "
                    f"Score: {txn['score']:.0f} | Return: {txn.get('return_pct', 0):+.2f}%"
                )

    report.append("\n" + "=" * 80)
    return "\n".join(report)


def save_backtest_results(results: List[Dict], mode: str, output_dir: str = "."):
    """
    Save backtest results to JSON and text report

    Args:
        results: List of backtest results
        mode: Risk mode
        output_dir: Directory to save files
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON
    json_path = Path(output_dir) / f"backtest_results_{mode}_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Saved JSON results: {json_path}")

    # Save text report
    report = generate_backtest_report(results, mode)
    txt_path = Path(output_dir) / f"backtest_report_{mode}_{timestamp}.txt"
    with open(txt_path, "w") as f:
        f.write(report)
    print(f"✅ Saved text report: {txt_path}")


if __name__ == "__main__":
    print("\n⚠️  This file should be run via CLI interface")
    print("Use: python src/stocks/backtest/run_backtest.py")
    print("Or see: python src/stocks/backtest/run_backtest.py --help\n")
