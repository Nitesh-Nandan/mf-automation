"""
Data Models and Type Definitions for Stock Technical Analysis
"""

from typing import TypedDict, Dict


class PricePoint(TypedDict):
    """Price at a specific date"""

    price: float
    date: str


class OHLCVData(TypedDict):
    """OHLCV candle data"""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class TechnicalIndicators(TypedDict):
    """All calculated technical indicators"""

    peak_90d: PricePoint
    low_90d: PricePoint
    change_from_peak_pct: float
    dma_50: float
    dma_100: float
    dma_200: float
    rsi: float
    avg_volume_20d: float
    current_volume: int
    volatility_2yr: float
    volatility_90d: float


class DipDepthScore(TypedDict):
    """Factor 1: Dip Depth scoring result"""

    score: float
    dip_percentage: float
    max_score: int


class HistoricalContextScore(TypedDict):
    """Factor 2: Historical Context scoring result"""

    score: float
    dip_ratio: float
    max_historical_dip: float
    max_score: int


class MeanReversionScore(TypedDict):
    """Factor 3: Mean Reversion scoring result"""

    score: float
    distance_from_dma: float
    dma_100: float
    max_score: int


class VolatilityScore(TypedDict):
    """Factor 4: Volatility scoring result"""

    score: float
    vol_ratio: float
    current_vol: float
    baseline_vol: float
    max_score: int


class RecoverySpeedScore(TypedDict):
    """Factor 5: Recovery Speed scoring result"""

    score: float
    avg_recovery_days: float
    recovery_count: int
    max_score: int


class TechnicalScore(TypedDict):
    """Factor 6: Technical Indicators scoring result"""

    score: float
    rsi: float
    rsi_score: float
    volume_ratio: float
    volume_score: float
    support_score: float
    max_score: int


class ScoreBreakdown(TypedDict):
    """Breakdown of all 6 factor scores"""

    dip_depth: DipDepthScore
    historical_context: HistoricalContextScore
    mean_reversion: MeanReversionScore
    volatility: VolatilityScore
    recovery_speed: RecoverySpeedScore
    technicals: TechnicalScore


class AnalysisResult(TypedDict):
    """Complete analysis result for a stock"""

    stock_name: str
    stock_symbol: str
    instrument_key: str
    current_price: float
    rsi: float
    dma_50: float
    dma_100: float
    dma_200: float
    peak_90d: PricePoint
    low_90d: PricePoint
    change_from_peak_pct: float
    final_score: float
    recommendation: str
    position_multiplier: float
    scores: ScoreBreakdown
    analysis_date: str
