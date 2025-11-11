"""
Comprehensive Backtest for Mutual Fund Dip Buying Strategy

This backtest simulates the dip-buying strategy over historical periods:
- Only dip buys (no SIP)
- Uses actual scoring algorithm from dip_analyzer.py
- Handles missing data with config defaults
- Generates detailed performance reports
"""

import json
import statistics
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    RECOMMENDATION_THRESHOLDS,
    RECOVERY_SPEED,
    TIME_WINDOWS,
    get_dip_depth_score,
    get_fund_category_score,
    get_historical_context_score,
    get_mean_reversion_score,
    get_volatility_score,
)
from data_fetcher import fetch_nav_data
from fund_loader import get_mf_funds


class BacktestEngine:
    """
    Backtest engine for mutual fund dip buying strategy

    Simulates historical performance by:
    1. Walking through time day-by-day
    2. Calculating scores using only past data (no future peeking)
    3. Making buy decisions based on score thresholds
    4. Tracking portfolio value over time
    """

    def __init__(
        self,
        fund_name: str,
        fund_code: str,
        fund_type: str,
        backtest_days: int = 730,  # 2 years
        initial_capital: float = 100000,
        investment_per_signal: float = 10000,
        mode: str = "conservative",
    ):
        """
        Initialize backtest engine

        Args:
            fund_name: Name of the fund
            fund_code: API code for the fund
            fund_type: Category (Small Cap, Mid Cap, etc.)
            backtest_days: Number of days to backtest
            initial_capital: Starting capital
            investment_per_signal: Amount to invest per buy signal
            mode: Risk mode (ultra_conservative, conservative, moderate, aggressive)
        """
        self.fund_name = fund_name
        self.fund_code = fund_code
        self.fund_type = fund_type
        self.backtest_days = backtest_days
        self.initial_capital = initial_capital
        self.investment_per_signal = investment_per_signal
        self.mode = mode
        self.threshold = RECOMMENDATION_THRESHOLDS.get(mode, 60)

        # Portfolio tracking
        self.capital = initial_capital
        self.units = 0.0
        self.transactions = []
        self.daily_portfolio_values = []

        # Historical data
        self.nav_data = []
        self.data_fetch_error = None

    def fetch_historical_data(self, lookback_days: int = 1095) -> bool:
        """
        Fetch historical NAV data for backtesting

        Args:
            lookback_days: Total days to fetch (includes backtest + analysis buffer)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Fetch more data than backtest period to allow for lookback windows
            # Add extra buffer to account for API not returning exact number of days
            total_days = (
                self.backtest_days + TIME_WINDOWS["historical_analysis_days"] + 365
            )
            self.nav_data = fetch_nav_data(self.fund_code, days=total_days)

            if not self.nav_data:
                self.data_fetch_error = "No data available"
                return False

            # Sort ascending (oldest first)
            self.nav_data.sort(key=lambda x: x["date"])
            return True

        except Exception as e:
            self.data_fetch_error = str(e)
            return False

    def calculate_score_at_point(
        self, current_index: int, nav_data_slice: List[Dict]
    ) -> Optional[Dict]:
        """
        Calculate dip buying score at a specific point in time
        Uses ONLY data available up to that point (no future peeking!)

        Args:
            current_index: Index in nav_data_slice representing current time
            nav_data_slice: Historical NAV data up to current point

        Returns:
            Dictionary with score and details, or None if insufficient data
        """
        if current_index < 0 or current_index >= len(nav_data_slice):
            return None

        current_date = nav_data_slice[current_index]["date"]
        current_nav = nav_data_slice[current_index]["nav"]

        # Define time windows
        analysis_days = TIME_WINDOWS["current_analysis_days"]
        historical_days = TIME_WINDOWS["historical_analysis_days"]

        # Get data for current analysis window (last N days from current point)
        analysis_start_date = current_date - timedelta(days=analysis_days)
        recent_data = [
            d
            for d in nav_data_slice[: current_index + 1]
            if d["date"] >= analysis_start_date
        ]

        # Get data for historical context (last M days from current point)
        historical_start_date = current_date - timedelta(days=historical_days)
        historical_data = [
            d
            for d in nav_data_slice[: current_index + 1]
            if d["date"] >= historical_start_date
        ]

        # Use all available data if less than requested window
        if len(recent_data) < 30:
            recent_data = nav_data_slice[: current_index + 1]

        if len(historical_data) < 90:
            historical_data = nav_data_slice[: current_index + 1]

        # Need minimum data points for meaningful analysis
        if len(recent_data) < 30 or len(historical_data) < 30:
            return None  # Truly insufficient data

        # ===== FACTOR 1: DIP DEPTH (0-40 points) =====
        peak_entry = max(recent_data, key=lambda x: x["nav"])
        peak_nav = peak_entry["nav"]
        dip_percentage = ((peak_nav - current_nav) / peak_nav) * 100
        dip_score = get_dip_depth_score(dip_percentage)

        # Skip if below minimum threshold
        if dip_percentage < TIME_WINDOWS["min_dip_threshold"]:
            return None

        # ===== FACTOR 2: HISTORICAL CONTEXT (0-13 points) =====
        max_historical_dip = self._calculate_max_historical_dip(historical_data)

        # Handle insufficient historical data with reasonable defaults
        # If historical data is limited, use current dip or config minimum
        if max_historical_dip < TIME_WINDOWS["min_dip_threshold"]:
            # Default: assume current dip is representative, or use 12% (typical correction)
            max_historical_dip = max(dip_percentage, 12.0)

        historical_score, dip_ratio = get_historical_context_score(
            dip_percentage, max_historical_dip
        )

        # ===== FACTOR 3: MEAN REVERSION (0-13 points) =====
        mean_nav = sum(d["nav"] for d in recent_data) / len(recent_data)
        mean_score, deviation = get_mean_reversion_score(current_nav, mean_nav)

        # ===== FACTOR 4: VOLATILITY (0-11 points) =====
        volatility = self._calculate_volatility(historical_data)
        volatility_score = get_volatility_score(volatility)

        # ===== FACTOR 5: RECOVERY SPEED (0-13 points) =====
        # For backtest, use config default to avoid expensive calculation
        # In production, this would be calculated from full history
        avg_recovery_days = 45  # Default from config (between 30-60 day thresholds)
        has_history = (
            len(historical_data) >= 90
        )  # At least 90 days for meaningful history
        recovery_score = self._get_recovery_speed_score_fast(
            avg_recovery_days, has_history
        )

        # ===== FACTOR 6: FUND CATEGORY (0-10 points) =====
        category_score = get_fund_category_score(self.fund_type)

        # ===== TOTAL SCORE =====
        total_score = (
            dip_score
            + historical_score
            + mean_score
            + volatility_score
            + recovery_score
            + category_score
        )

        return {
            "date": current_date,
            "nav": current_nav,
            "score": round(total_score, 2),
            "dip_percentage": round(dip_percentage, 2),
            "peak_nav": round(peak_nav, 4),
            "mean_nav": round(mean_nav, 4),
            "volatility": round(volatility, 2),
            "max_historical_dip": round(max_historical_dip, 2),
            "breakdown": {
                "dip_depth": dip_score,
                "historical_context": historical_score,
                "mean_reversion": round(mean_score, 2),
                "volatility": volatility_score,
                "recovery_speed": recovery_score,
                "fund_category": category_score,
            },
        }

    def _calculate_max_historical_dip(self, historical_data: List[Dict]) -> float:
        """Calculate maximum historical dip from data"""
        if len(historical_data) < 2:
            return 0.0

        max_dip = 0.0
        running_max_nav = historical_data[0]["nav"]

        for entry in historical_data:
            current_nav = entry["nav"]
            if current_nav > running_max_nav:
                running_max_nav = current_nav

            dip = ((running_max_nav - current_nav) / running_max_nav) * 100
            if dip > max_dip:
                max_dip = dip

        return max_dip

    def _calculate_volatility(self, nav_data: List[Dict]) -> float:
        """Calculate annualized volatility"""
        if len(nav_data) < 2:
            return 0.0

        returns = []
        for i in range(1, len(nav_data)):
            daily_return = (nav_data[i]["nav"] - nav_data[i - 1]["nav"]) / nav_data[
                i - 1
            ]["nav"]
            returns.append(daily_return)

        if len(returns) < 2:
            return 0.0

        volatility = statistics.stdev(returns) * (252**0.5) * 100
        return volatility

    def _get_recovery_speed_score_fast(
        self, avg_recovery_days: float, has_history: bool
    ) -> int:
        """Fast recovery speed scoring using config defaults"""
        if not has_history:
            return RECOVERY_SPEED["no_history_score"]

        for threshold in sorted(RECOVERY_SPEED["thresholds"].keys()):
            if avg_recovery_days <= threshold:
                return RECOVERY_SPEED["thresholds"][threshold]

        return RECOVERY_SPEED["slow_recovery_score"]

    def run_backtest(self, evaluation_interval: int = 7) -> Dict:
        """
        Run the backtest simulation

        Args:
            evaluation_interval: Days between evaluations (default: 7 = weekly)

        Returns:
            Dictionary with backtest results
        """
        if not self.nav_data:
            if not self.fetch_historical_data():
                return {"error": f"Failed to fetch data: {self.data_fetch_error}"}

        # Define backtest period (last N days)
        backtest_start_date = self.nav_data[-1]["date"] - timedelta(
            days=self.backtest_days
        )
        backtest_indices = [
            i for i, d in enumerate(self.nav_data) if d["date"] >= backtest_start_date
        ]

        if len(backtest_indices) < 30:
            return {"error": "Insufficient data for backtest period"}

        # Baseline: buy-and-hold from start
        baseline_start_nav = self.nav_data[backtest_indices[0]]["nav"]
        baseline_units = self.initial_capital / baseline_start_nav

        # Run simulation - evaluate at intervals
        for i in range(0, len(backtest_indices), evaluation_interval):
            current_idx = backtest_indices[i]

            # Need minimum data points (use defaults if less than ideal)
            min_data_needed = max(90, TIME_WINDOWS["current_analysis_days"] // 2)
            if current_idx < min_data_needed:
                continue  # Only skip if truly insufficient data

            # Calculate score at this point (uses defaults for missing historical data)
            score_result = self.calculate_score_at_point(
                current_idx, self.nav_data[: current_idx + 1]
            )

            if not score_result:
                continue

            # Make buy decision
            if (
                score_result["score"] >= self.threshold
                and self.capital >= self.investment_per_signal
            ):
                self._execute_buy(score_result)

            # Track portfolio value
            current_nav = score_result["nav"]
            portfolio_value = (self.units * current_nav) + self.capital
            self.daily_portfolio_values.append(
                {
                    "date": score_result["date"],
                    "nav": current_nav,
                    "portfolio_value": portfolio_value,
                    "units": self.units,
                    "capital": self.capital,
                }
            )

        # Calculate final results
        final_nav = self.nav_data[-1]["nav"]
        final_date = self.nav_data[-1]["date"]

        strategy_final_value = (self.units * final_nav) + self.capital
        strategy_return_pct = (
            (strategy_final_value - self.initial_capital) / self.initial_capital
        ) * 100

        baseline_final_value = baseline_units * final_nav
        baseline_return_pct = (
            (baseline_final_value - self.initial_capital) / self.initial_capital
        ) * 100

        # Calculate metrics
        total_invested = sum(t["amount_invested"] for t in self.transactions)
        avg_buy_nav = total_invested / self.units if self.units > 0 else 0

        return {
            "fund_name": self.fund_name,
            "fund_code": self.fund_code,
            "fund_type": self.fund_type,
            "mode": self.mode,
            "threshold": self.threshold,
            # Period
            "backtest_start_date": backtest_start_date.strftime("%d-%m-%Y"),
            "backtest_end_date": final_date.strftime("%d-%m-%Y"),
            "backtest_days": self.backtest_days,
            "initial_capital": self.initial_capital,
            # Strategy results
            "num_transactions": len(self.transactions),
            "total_invested": round(total_invested, 2),
            "units_accumulated": round(self.units, 4),
            "avg_buy_nav": round(avg_buy_nav, 2),
            "capital_remaining": round(self.capital, 2),
            "strategy_final_value": round(strategy_final_value, 2),
            "strategy_return_pct": round(strategy_return_pct, 2),
            # Baseline results
            "baseline_buy_nav": round(baseline_start_nav, 4),
            "baseline_units": round(baseline_units, 4),
            "baseline_final_value": round(baseline_final_value, 2),
            "baseline_return_pct": round(baseline_return_pct, 2),
            # Comparison
            "outperformance": round(strategy_return_pct - baseline_return_pct, 2),
            "final_nav": round(final_nav, 4),
            # Details
            "transactions": self.transactions,
            "portfolio_history": self.daily_portfolio_values,
            "error": None,
        }

    def _execute_buy(self, score_result: Dict):
        """Execute a buy transaction"""
        amount = min(self.investment_per_signal, self.capital)
        nav = score_result["nav"]
        units = amount / nav

        self.units += units
        self.capital -= amount

        self.transactions.append(
            {
                "date": score_result["date"].strftime("%d-%m-%Y"),
                "nav": round(nav, 4),
                "score": score_result["score"],
                "dip_percentage": score_result["dip_percentage"],
                "amount_invested": round(amount, 2),
                "units_bought": round(units, 4),
                "breakdown": score_result["breakdown"],
            }
        )


def run_backtest_for_fund(
    fund: Dict,
    backtest_days: int = 730,
    initial_capital: float = 100000,
    investment_per_signal: float = 10000,
    mode: str = "conservative",
) -> Dict:
    """
    Run backtest for a single fund

    Args:
        fund: Fund dictionary from mf_funds.csv
        backtest_days: Number of days to backtest
        initial_capital: Starting capital
        investment_per_signal: Amount per buy signal
        mode: Risk mode

    Returns:
        Backtest results dictionary
    """
    engine = BacktestEngine(
        fund_name=fund["fund_name"],
        fund_code=fund["code"],
        fund_type=fund["type"],
        backtest_days=backtest_days,
        initial_capital=initial_capital,
        investment_per_signal=investment_per_signal,
        mode=mode,
    )

    return engine.run_backtest()


def run_backtest_all_funds(
    backtest_days: int = 730,
    initial_capital: float = 100000,
    investment_per_signal: float = 10000,
    mode: str = "conservative",
) -> List[Dict]:
    """
    Run backtest on all funds

    Args:
        backtest_days: Number of days to backtest (default: 730 = 2 years)
        initial_capital: Starting capital per fund
        investment_per_signal: Amount to invest per buy signal
        mode: Risk mode

    Returns:
        List of backtest results
    """
    funds = get_mf_funds()
    results = []

    print(f"\n{'='*80}")
    print(f"🔬 BACKTESTING DIP BUYING STRATEGY - {mode.upper()} MODE")
    print(f"{'='*80}")
    print(f"Period: Last {backtest_days} days (~{backtest_days//365} years)")
    print(f"Initial Capital: ₹{initial_capital:,.0f} per fund")
    print(f"Investment per Signal: ₹{investment_per_signal:,.0f}")
    print(f"Buy Threshold: {RECOMMENDATION_THRESHOLDS[mode]} points")
    print(f"{'='*80}\n")

    for i, fund in enumerate(funds, 1):
        if not fund.get("code"):
            print(f"⚠️  Skipping {fund['fund_name']} - No API code")
            continue

        print(f"[{i}/{len(funds)}] Backtesting {fund['fund_name']}...")

        try:
            result = run_backtest_for_fund(
                fund=fund,
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
                    f"  ✅ Completed | Transactions: {result['num_transactions']} | "
                    f"Return: {result['strategy_return_pct']:+.2f}% | "
                    f"vs Baseline: {result['outperformance']:+.2f}%"
                )

        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")

    return results


def generate_backtest_report(results: List[Dict], mode: str) -> str:
    """
    Generate comprehensive backtest report

    Args:
        results: List of backtest results
        mode: Risk mode used

    Returns:
        Formatted report string
    """
    if not results:
        return "No results to report"

    report = []
    report.append("\n" + "=" * 80)
    report.append("📊 COMPREHENSIVE BACKTEST REPORT")
    report.append("=" * 80)
    report.append(f"\nGenerated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    report.append(f"Mode: {mode.upper()}")
    report.append(f"Threshold: {RECOMMENDATION_THRESHOLDS[mode]} points")
    report.append(f"Backtest Period: {results[0]['backtest_days']} days")
    report.append(f"Funds Analyzed: {len(results)}")

    # Overall statistics
    report.append("\n" + "=" * 80)
    report.append("📈 OVERALL PERFORMANCE SUMMARY")
    report.append("=" * 80)

    total_transactions = sum(r["num_transactions"] for r in results)
    total_invested = sum(r["total_invested"] for r in results)
    avg_strategy_return = sum(r["strategy_return_pct"] for r in results) / len(results)
    avg_baseline_return = sum(r["baseline_return_pct"] for r in results) / len(results)
    avg_outperformance = sum(r["outperformance"] for r in results) / len(results)

    winning_funds = [r for r in results if r["outperformance"] > 0]
    losing_funds = [r for r in results if r["outperformance"] <= 0]
    win_rate = (len(winning_funds) / len(results)) * 100

    report.append(f"\nTotal Buy Signals Across All Funds: {total_transactions}")
    report.append(f"Total Capital Invested: ₹{total_invested:,.2f}")
    report.append(f"Average Strategy Return: {avg_strategy_return:+.2f}%")
    report.append(f"Average Baseline Return: {avg_baseline_return:+.2f}%")
    report.append(f"Average Outperformance: {avg_outperformance:+.2f}%")
    report.append(
        f"Win Rate: {win_rate:.1f}% ({len(winning_funds)}/{len(results)} funds)"
    )

    # Performance verdict
    report.append("\n" + "-" * 80)
    if avg_outperformance > 2:
        report.append("🎉 VERDICT: Strategy SIGNIFICANTLY OUTPERFORMS buy-and-hold!")
    elif avg_outperformance > 0:
        report.append("✅ VERDICT: Strategy OUTPERFORMS buy-and-hold")
    elif avg_outperformance > -2:
        report.append("➖ VERDICT: Strategy performs SIMILARLY to buy-and-hold")
    else:
        report.append("❌ VERDICT: Strategy UNDERPERFORMS buy-and-hold")
    report.append("-" * 80)

    # Top performers
    report.append("\n" + "=" * 80)
    report.append("🏆 TOP 5 PERFORMERS (by outperformance)")
    report.append("=" * 80)
    report.append(f"{'Fund':<40} {'Transactions':<13} {'Return':<10} {'Outperf':<10}")
    report.append("-" * 80)

    top_performers = sorted(results, key=lambda x: x["outperformance"], reverse=True)[
        :5
    ]
    for r in top_performers:
        fund_name = r["fund_name"][:38]
        report.append(
            f"{fund_name:<40} {r['num_transactions']:<13} "
            f"{r['strategy_return_pct']:>8.2f}% {r['outperformance']:>8.2f}%"
        )

    # Bottom performers
    report.append("\n" + "=" * 80)
    report.append("⚠️  BOTTOM 3 PERFORMERS")
    report.append("=" * 80)
    report.append(f"{'Fund':<40} {'Transactions':<13} {'Return':<10} {'Outperf':<10}")
    report.append("-" * 80)

    bottom_performers = sorted(results, key=lambda x: x["outperformance"])[:3]
    for r in bottom_performers:
        fund_name = r["fund_name"][:38]
        report.append(
            f"{fund_name:<40} {r['num_transactions']:<13} "
            f"{r['strategy_return_pct']:>8.2f}% {r['outperformance']:>8.2f}%"
        )

    # Detailed fund-by-fund breakdown
    report.append("\n" + "=" * 80)
    report.append("📋 DETAILED FUND-BY-FUND ANALYSIS")
    report.append("=" * 80)

    for r in sorted(results, key=lambda x: x["outperformance"], reverse=True):
        report.append(f"\n{'-'*80}")
        report.append(f"Fund: {r['fund_name']}")
        report.append(f"Type: {r['fund_type']}")
        report.append(f"{'-'*80}")
        report.append(f"Period: {r['backtest_start_date']} to {r['backtest_end_date']}")
        report.append(f"\n📊 Strategy Performance:")
        report.append(f"  Buy Signals: {r['num_transactions']}")
        report.append(f"  Total Invested: ₹{r['total_invested']:,.2f}")
        report.append(f"  Units Accumulated: {r['units_accumulated']:.4f}")
        report.append(f"  Average Buy NAV: ₹{r['avg_buy_nav']:.2f}")
        report.append(f"  Final Value: ₹{r['strategy_final_value']:,.2f}")
        report.append(f"  Return: {r['strategy_return_pct']:+.2f}%")
        report.append(f"\n📈 Baseline (Buy & Hold):")
        report.append(f"  Buy NAV: ₹{r['baseline_buy_nav']:.2f}")
        report.append(f"  Final Value: ₹{r['baseline_final_value']:,.2f}")
        report.append(f"  Return: {r['baseline_return_pct']:+.2f}%")
        report.append(f"\n🎯 Outperformance: {r['outperformance']:+.2f}%")

        # Show transactions if any
        if r["transactions"]:
            report.append(f"\n💰 Transactions ({len(r['transactions'])}):")
            report.append(
                f"  {'Date':<12} {'Score':<7} {'Dip%':<7} {'NAV':<10} {'Invested':<12}"
            )
            for t in r["transactions"][:5]:  # Show first 5
                report.append(
                    f"  {t['date']:<12} {t['score']:<7.1f} {t['dip_percentage']:<7.2f} "
                    f"₹{t['nav']:<9.2f} ₹{t['amount_invested']:>10,.0f}"
                )
            if len(r["transactions"]) > 5:
                report.append(
                    f"  ... and {len(r['transactions']) - 5} more transactions"
                )

    # Market conditions insights
    report.append("\n" + "=" * 80)
    report.append("💡 INSIGHTS & RECOMMENDATIONS")
    report.append("=" * 80)

    # Analyze transaction frequency
    funds_with_signals = [r for r in results if r["num_transactions"] > 0]
    funds_without_signals = [r for r in results if r["num_transactions"] == 0]

    report.append(f"\n📊 Buy Signal Frequency:")
    report.append(f"  Funds with buy signals: {len(funds_with_signals)}/{len(results)}")
    report.append(f"  Funds without signals: {len(funds_without_signals)}")

    if funds_with_signals:
        avg_signals = sum(r["num_transactions"] for r in funds_with_signals) / len(
            funds_with_signals
        )
        report.append(f"  Average signals per active fund: {avg_signals:.1f}")

    if len(funds_without_signals) > len(funds_with_signals):
        report.append(
            f"\n⚠️  Most funds had NO buy signals - threshold may be too high for this period"
        )
        report.append(
            f"  Consider: Lowering threshold or testing more volatile market periods"
        )

    # Analyze by fund type
    report.append(f"\n📊 Performance by Fund Type:")
    fund_types = {}
    for r in results:
        ft = r["fund_type"]
        if ft not in fund_types:
            fund_types[ft] = []
        fund_types[ft].append(r)

    for ft, ft_results in fund_types.items():
        avg_out = sum(r["outperformance"] for r in ft_results) / len(ft_results)
        avg_txns = sum(r["num_transactions"] for r in ft_results) / len(ft_results)
        report.append(
            f"  {ft:<20}: {avg_out:+.2f}% avg outperformance, {avg_txns:.1f} avg signals"
        )

    # Final recommendations
    report.append(f"\n💡 Recommendations:")
    if avg_outperformance > 0 and win_rate > 50:
        report.append(
            f"  ✅ Strategy is EFFECTIVE - continue using with current settings"
        )
        report.append(
            f"  ✅ Win rate of {win_rate:.0f}% indicates consistent outperformance"
        )
    elif avg_outperformance > 0:
        report.append(f"  ⚠️  Strategy outperforms on average but inconsistently")
        report.append(f"  💡 Consider refining scoring for specific fund types")
    else:
        report.append(f"  ⚠️  Strategy needs refinement for this market period")
        report.append(
            f"  💡 Consider: Adjusting thresholds or testing in different market conditions"
        )

    if total_transactions < len(results) * 2:
        report.append(
            f"  💡 Low signal frequency - consider more aggressive mode for more opportunities"
        )

    report.append("\n" + "=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80 + "\n")

    return "\n".join(report)


def save_backtest_results(results: List[Dict], mode: str, output_dir: str = "."):
    """
    Save backtest results to files

    Args:
        results: List of backtest results
        mode: Risk mode used
        output_dir: Directory to save files
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed JSON results
    json_file = output_path / f"backtest_results_{mode}_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Saved detailed results: {json_file}")

    # Save text report
    report = generate_backtest_report(results, mode)
    report_file = output_path / f"backtest_report_{mode}_{timestamp}.txt"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"💾 Saved report: {report_file}")

    return json_file, report_file


def main():
    """Main function to run backtest"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Backtest mutual fund dip buying strategy"
    )
    parser.add_argument(
        "--mode",
        choices=["ultra_conservative", "conservative", "moderate", "aggressive"],
        default="conservative",
        help="Risk mode (default: conservative)",
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
        help="Initial capital per fund (default: 100000)",
    )
    parser.add_argument(
        "--investment",
        type=float,
        default=10000,
        help="Investment per buy signal (default: 10000)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=".",
        help="Output directory for results (default: current directory)",
    )

    args = parser.parse_args()

    # Run backtest
    results = run_backtest_all_funds(
        backtest_days=args.days,
        initial_capital=args.capital,
        investment_per_signal=args.investment,
        mode=args.mode,
    )

    if not results:
        print("\n❌ No results generated - check data availability")
        return

    # Print report
    report = generate_backtest_report(results, args.mode)
    print(report)

    # Save results
    save_backtest_results(results, args.mode, args.output)


if __name__ == "__main__":
    main()
