"""
Stock Technical Analysis Backtest Module

Backtest the dip-buying strategy over historical periods.
"""

from .backtest_stock_strategy import (
    StockBacktestEngine,
    run_backtest_for_stock,
    generate_backtest_report,
    save_backtest_results,
    RECOMMENDATION_THRESHOLDS,
)

__all__ = [
    "StockBacktestEngine",
    "run_backtest_for_stock",
    "generate_backtest_report",
    "save_backtest_results",
    "RECOMMENDATION_THRESHOLDS",
]








