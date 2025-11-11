"""
Mutual Fund Dip Analyzer Package

A comprehensive 6-factor algorithm for identifying optimal dip-buying opportunities
in Indian mutual funds.

Main Components:
- dip_analyzer: Core analysis engine
- trend_analyzer: Current dip detection
- history_analyzer: Historical context analysis
- scoring: 6-factor scoring system
- data_fetcher: NAV data retrieval
- fund_loader: Fund portfolio loader
"""

from .config import (
    RECOMMENDATION_THRESHOLDS,
    SCORING_BANDS,
    TIME_WINDOWS,
)
from .dip_analyzer import (
    analyze_all_funds,
    analyze_dip_opportunity,
    print_analysis_summary,
    print_detailed_analysis,
)

__version__ = "2.0.0"
__author__ = "MF Analysis Bot"

__all__ = [
    # Main analysis functions
    "analyze_dip_opportunity",
    "analyze_all_funds",
    "print_analysis_summary",
    "print_detailed_analysis",
    # Configuration
    "TIME_WINDOWS",
    "RECOMMENDATION_THRESHOLDS",
    "SCORING_BANDS",
]
