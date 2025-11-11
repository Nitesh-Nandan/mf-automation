"""
Type definitions for Mutual Fund Analyzer

Provides TypedDict classes for better type safety and IDE autocomplete.
"""

from datetime import datetime
from typing import Literal, Optional, TypedDict

# Type aliases
AnalysisMode = Literal["ultra_conservative", "conservative", "moderate", "aggressive"]
Recommendation = Literal["STRONG BUY", "BUY", "MODERATE BUY", "WEAK BUY", "HOLD"]
Confidence = Literal["Very High", "High", "Medium", "Low", "None"]


class NAVEntry(TypedDict):
    """Single NAV data point"""

    date: datetime
    nav: float


class FundInfo(TypedDict):
    """Mutual fund information from CSV"""

    fund_name: str
    type: str
    code: str
    url: str


class ScoreDetails(TypedDict):
    """Score details for a single factor"""

    score: float
    max: int
    factor: str


class DipDepthScore(ScoreDetails):
    """Dip depth score details"""

    value: float  # Current dip percentage


class HistoricalContextScore(ScoreDetails):
    """Historical context score details"""

    current_vs_max_ratio: float


class MeanReversionScore(ScoreDetails):
    """Mean reversion score details"""

    below_mean_pct: float


class VolatilityScore(ScoreDetails):
    """Volatility score details"""

    volatility: float


class RecoverySpeedScore(ScoreDetails):
    """Recovery speed score details"""

    avg_recovery_days: float
    recovery_count: int


class FundCategoryScore(ScoreDetails):
    """Fund category score details"""

    category: str


class ScoreBreakdown(TypedDict):
    """Complete score breakdown for all factors"""

    dip_depth: DipDepthScore
    historical_context: HistoricalContextScore
    mean_reversion: MeanReversionScore
    volatility: VolatilityScore
    recovery_speed: RecoverySpeedScore
    fund_category: FundCategoryScore


class CurrentAnalysis(TypedDict):
    """Current dip analysis results"""

    fund_name: str
    fund_code: str
    is_in_dip: bool
    current_nav: float
    current_date: str
    peak_nav: float
    peak_date: str
    bottom_nav: float
    bottom_date: str
    mean_nav: float
    dip_from_peak_percentage: float
    days_analyzed: int
    error: Optional[str]


class MaxDipInfo(TypedDict):
    """Information about maximum historical dip"""

    peak_nav: float
    peak_date: str
    bottom_nav: float
    bottom_date: str
    dip_percentage: float


class HistoricalAnalysis(TypedDict):
    """Historical dip analysis results"""

    fund_name: str
    fund_code: str
    days_analyzed: int
    current_nav: float
    current_date: str
    peak_nav: float
    peak_date: str
    bottom_nav: float
    bottom_date: str
    mean_nav: float
    dip_from_peak_percentage: float
    is_in_dip: bool
    max_historical_dip: float
    max_dip_info: MaxDipInfo
    has_10_percent_dip: bool
    error: Optional[str]


class RecoveryData(TypedDict):
    """Recovery speed analysis data"""

    avg_recovery_days: float
    recovery_count: int
    has_history: bool


class AnalysisResult(TypedDict):
    """Complete analysis result for a fund"""

    fund_name: str
    fund_code: str
    fund_type: str
    total_score: float
    recommendation: Recommendation
    allocation_percentage: float
    confidence: Confidence
    mode: AnalysisMode
    threshold: int
    triggers_buy: bool
    score_breakdown: ScoreBreakdown
    current_analysis: CurrentAnalysis
    historical_analysis: HistoricalAnalysis
    error: Optional[str]


class EmailFundData(TypedDict):
    """Fund data formatted for email report"""

    fund_name: str
    current_nav: float
    dip_percentage: float
    recent_low_nav: float
    recent_low_date: str
    recent_high_nav: float
    recent_high_date: str
    recent_mean_nav: float
    historical_low_nav: float
    historical_low_date: str
    historical_high_nav: float
    historical_high_date: str
    historical_mean_nav: float
    score: float
    verdict: str
