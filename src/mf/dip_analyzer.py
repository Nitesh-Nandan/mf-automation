"""
Mutual Fund Dip Analyzer - Refactored

Clean, maintainable 6-factor algorithm for identifying optimal dip-buying opportunities.

Main Components:
- analyze_dip_opportunity: Analyze a single fund
- analyze_all_funds: Analyze all funds in portfolio
- print_analysis_summary: Display summary results
- print_detailed_analysis: Display detailed analysis for a fund
"""

from datetime import datetime
from typing import Dict, List

from .config import RECOMMENDATION_THRESHOLDS, TIME_WINDOWS, get_recommendation
from .data_fetcher import fetch_nav_data
from .exceptions import DataFetchError, InvalidModeError
from .fund_loader import get_mf_funds
from .history_analyzer import analyze_max_historical_dip
from .scoring import calculate_all_scores
from .trend_analyzer import analyze_fund_dip
from .types import AnalysisMode, AnalysisResult
from .utils import clamp, format_currency, format_percentage, safe_round


def analyze_dip_opportunity(
    fund_name: str,
    code: str,
    fund_type: str,
    analysis_days: int = None,
    historical_days: int = None,
    mode: AnalysisMode = "conservative",
) -> AnalysisResult:
    """
    Comprehensive 6-factor dip-buying analysis

    Calculates a 0-100 score based on:
    1. Dip Depth (0-40 pts) - How far from peak
    2. Historical Context (0-13 pts) - Compared to past dips
    3. Mean Reversion (0-13 pts) - Below average price
    4. Volatility (0-11 pts) - Risk/reward balance
    5. Recovery Speed (0-13 pts) - Historical resilience
    6. Fund Type (0-10 pts) - Category adjustment

    Args:
        fund_name: Name of the mutual fund
        code: API code for the fund
        fund_type: Category (Small Cap, Mid Cap, Large Cap, etc.)
        analysis_days: Lookback period for current analysis (default from config)
        historical_days: Lookback period for historical context (default from config)
        mode: Risk level - 'ultra_conservative', 'conservative', 'moderate', 'aggressive'

    Returns:
        Dictionary containing:
        - total_score: 0-100 overall score
        - recommendation: STRONG BUY, BUY, MODERATE BUY, WEAK BUY, or HOLD
        - triggers_buy: Boolean if score meets threshold
        - allocation_percentage: Suggested capital allocation
        - score_breakdown: Individual factor scores
        - Full analysis details
    """
    # Use config defaults if not specified
    if analysis_days is None:
        analysis_days = TIME_WINDOWS["current_analysis_days"]
    if historical_days is None:
        historical_days = TIME_WINDOWS["historical_analysis_days"]

    try:
        # Step 1: Fetch NAV data ONCE (optimization - was 3 calls, now 1!)
        nav_data = fetch_nav_data(code, historical_days)

        # Sort by date ASCENDING (oldest first) - sorted once, used everywhere
        nav_data.sort(key=lambda x: x["date"])

        # Step 2: Get current dip analysis (using pre-fetched data)
        current_analysis = analyze_fund_dip(
            fund_name=fund_name,
            code=code,
            dip_percentage=TIME_WINDOWS["min_dip_threshold"],
            days=analysis_days,
            nav_data=nav_data,  # Pass pre-fetched data
        )

        if current_analysis.get("error"):
            return {"error": current_analysis["error"]}

        # Step 3: Get historical maximum dip (using pre-fetched data)
        historical_analysis = analyze_max_historical_dip(
            fund_name=fund_name,
            code=code,
            days=historical_days,
            nav_data=nav_data,  # Pass pre-fetched data
        )

        if historical_analysis.get("error"):
            return {"error": historical_analysis["error"]}

        # Step 4: Calculate all 6 factor scores (using same nav_data)
        score_breakdown, total_score = calculate_all_scores(
            current_analysis=current_analysis,
            historical_analysis=historical_analysis,
            nav_data=nav_data,
            fund_type=fund_type,
        )

        # Step 5: Generate recommendation
        final_score = clamp(total_score, 0, 100)
        triggers_buy, recommendation, allocation, confidence = get_recommendation(
            final_score, mode
        )

        # Step 6: Return complete analysis
        return {
            "fund_name": fund_name,
            "fund_code": code,
            "fund_type": fund_type,
            "total_score": safe_round(final_score, 2),
            "recommendation": recommendation,
            "allocation_percentage": allocation,
            "confidence": confidence,
            "mode": mode,
            "threshold": RECOMMENDATION_THRESHOLDS.get(
                mode, RECOMMENDATION_THRESHOLDS["conservative"]
            ),
            "triggers_buy": triggers_buy,
            "score_breakdown": score_breakdown,  # type: ignore
            "current_analysis": current_analysis,  # type: ignore
            "historical_analysis": historical_analysis,  # type: ignore
            "error": None,
        }  # type: ignore

    except Exception as e:
        return {"fund_name": fund_name, "fund_code": code, "error": f"Error: {str(e)}"}


def analyze_all_funds(mode: AnalysisMode = "conservative") -> List[AnalysisResult]:
    """
    Analyze all funds from mf_funds.csv

    Args:
        mode: Risk level ('ultra_conservative', 'conservative', 'moderate', 'aggressive')

    Returns:
        List of analysis results sorted by score (highest first)

    Raises:
        InvalidModeError: If mode is not valid
    """
    # Validate mode
    if mode not in RECOMMENDATION_THRESHOLDS:
        raise InvalidModeError(mode, list(RECOMMENDATION_THRESHOLDS.keys()))

    funds = get_mf_funds()
    results: List[AnalysisResult] = []

    for fund in funds:
        if not fund.get("code"):
            continue

        result = analyze_dip_opportunity(
            fund_name=fund["fund_name"],
            code=fund["code"],
            fund_type=fund["type"],
            mode=mode,
        )

        if not result.get("error"):
            results.append(result)

    # Sort by score (highest first)
    results.sort(key=lambda x: x["total_score"], reverse=True)

    return results


def print_analysis_summary(results: List[AnalysisResult], mode: AnalysisMode):
    """Print summary - only for CLI usage"""
    threshold = RECOMMENDATION_THRESHOLDS.get(
        mode, RECOMMENDATION_THRESHOLDS["conservative"]
    )
    buy_signals = [r for r in results if r["triggers_buy"]]

    print(f"\nAnalysis: {len(results)} funds | {len(buy_signals)} buy signals")
    print(f"Mode: {mode} | Threshold: {threshold}")

    if buy_signals:
        print("\nBUY OPPORTUNITIES:")
        for r in buy_signals:
            print(
                f"  {r['fund_name']}: Score {r['total_score']:.1f} | {r['recommendation']}"
            )


def print_detailed_analysis(result: AnalysisResult):
    """Print detailed analysis - only for CLI usage"""
    print(f"\nDetailed: {result['fund_name']}")
    print(f"Score: {result['total_score']:.1f}/100 | {result['recommendation']}")
    print(f"Dip: {result['current_analysis']['dip_from_peak_percentage']:.1f}%")
    print(f"Triggers buy: {result['triggers_buy']}")


if __name__ == "__main__":
    import sys

    mode_arg = sys.argv[1] if len(sys.argv) > 1 else "conservative"

    if mode_arg not in RECOMMENDATION_THRESHOLDS:
        print(f"Invalid mode. Valid: {', '.join(RECOMMENDATION_THRESHOLDS.keys())}")
        sys.exit(1)

    mode: AnalysisMode = mode_arg  # type: ignore

    try:
        results = analyze_all_funds(mode=mode)
        print_analysis_summary(results, mode)
        if results and results[0]["triggers_buy"]:
            print_detailed_analysis(results[0])
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
