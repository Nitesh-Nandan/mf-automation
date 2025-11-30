"""
Technical Stock Dip-Buying Analysis
Main orchestrator - fetches data and coordinates scoring
"""

import statistics
from datetime import datetime, timedelta
from typing import List, Optional

from .historical_data import get_historical_data, get_ltp, IntervalUnit
from .models import OHLCVData, TechnicalIndicators, AnalysisResult, ScoreBreakdown
from .TechnicalScore import (
    score_dip_depth,
    score_historical_context,
    score_mean_reversion,
    score_volatility,
    score_recovery_speed,
    score_technicals,
    get_recommendation,
)


class TechnicalAnalysis:
    """
    Technical Dip-Buying Analyzer for Quality Stocks

    Orchestrates data fetching (via historical_data.py) and scoring (via TechnicalScore.py)

    Implements 6-factor scoring system (0-100 points):
    1. Dip Depth (0-20 pts)
    2. Historical Context (0-25 pts)
    3. Mean Reversion (0-15 pts)
    4. Volatility (0-10 pts)
    5. Recovery Speed (0-20 pts)
    6. Technicals (0-10 pts)
    """

    def __init__(self, stock_name: str, stock_symbol: str, instrument_key: str):
        """
        Initialize analyzer for a stock

        Args:
            stock_name: Full name (e.g., "Asian Paints")
            stock_symbol: NSE symbol (e.g., "ASIANPAINT")
            instrument_key: Upstox instrument key (e.g., "NSE_EQ|INE021A01026")
        """
        self.stock_name = stock_name
        self.stock_symbol = stock_symbol
        self.instrument_key = instrument_key
        self.raw_data: List[List] = []
        self.current_price: float = 0.0

    def analyze(self) -> Optional[AnalysisResult]:
        """
        Main analysis method - orchestrates all calculations

        Returns:
            AnalysisResult or None if error
        """
        # Step 1: Fetch data using historical_data.py module
        if not self._fetch_data():
            return None

        # Step 2: Transform data
        price_data = self._transform_data()

        if len(price_data) < 100:
            print(f"Error: Insufficient data ({len(price_data)} days, need 100+)")
            return None

        # Step 3: Calculate technical indicators
        indicators = self._calculate_indicators(price_data)

        # Step 4: Calculate all 6 factor scores (using TechnicalScore module)
        scores = self._calculate_all_scores(price_data, indicators)

        # Step 5: Calculate total score
        total_score = sum(
            [
                scores["dip_depth"]["score"],
                scores["historical_context"]["score"],
                scores["mean_reversion"]["score"],
                scores["volatility"]["score"],
                scores["recovery_speed"]["score"],
                scores["technicals"]["score"],
            ]
        )

        # Step 6: Generate recommendation
        recommendation, multiplier = get_recommendation(total_score)

        # Step 7: Build result
        return {
            "stock_name": self.stock_name,
            "stock_symbol": self.stock_symbol,
            "instrument_key": self.instrument_key,
            "current_price": self.current_price,
            "rsi": indicators["rsi"],
            "dma_50": indicators["dma_50"],
            "dma_100": indicators["dma_100"],
            "dma_200": indicators["dma_200"],
            "peak_90d": indicators["peak_90d"],
            "low_90d": indicators["low_90d"],
            "change_from_peak_pct": indicators["change_from_peak_pct"],
            "final_score": round(total_score, 2),
            "recommendation": recommendation,
            "position_multiplier": multiplier,
            "scores": scores,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # =========================================================================
    # DATA FETCHING (Using historical_data.py module)
    # =========================================================================

    def _fetch_data(self) -> bool:
        """Fetch historical data (2 years) and current price using historical_data module"""
        try:
            # Calculate dates
            to_date = datetime.now().strftime("%Y-%m-%d")
            from_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

            # Fetch historical data
            hist_response = get_historical_data(
                self.instrument_key,
                to_date,
                from_date,
                unit=IntervalUnit.DAYS,
                interval="1",
            )

            if not hist_response:
                print(f"Error: Failed to fetch data for {self.stock_symbol}")
                return False

            self.raw_data = hist_response.get("data", {}).get("candles", [])

            if not self.raw_data:
                print(f"Error: No candle data for {self.stock_symbol}")
                return False

            # Get current price
            ltp_response = get_ltp(self.instrument_key)

            if ltp_response and ltp_response.get("data"):
                self.current_price = (
                    ltp_response.get("data", {})
                    .get(self.instrument_key, {})
                    .get("last_price", 0.0)
                )

            # Fallback to latest close if LTP not available
            if self.current_price == 0.0 and self.raw_data:
                self.current_price = self.raw_data[0][4]

            return True

        except Exception as e:
            print(f"Error fetching data: {e}")
            return False

    # =========================================================================
    # DATA TRANSFORMATION
    # =========================================================================

    def _transform_data(self) -> List[OHLCVData]:
        """
        Transform Upstox candle data to OHLCVData format

        Upstox format: [timestamp, open, high, low, close, volume, oi]
        Returns: List of dicts sorted by date (oldest first)
        """
        transformed = []
        for candle in self.raw_data:
            transformed.append(
                {
                    "date": candle[0].split("T")[0],  # Extract date from timestamp
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": int(candle[5]) if len(candle) > 5 else 0,
                }
            )

        # Sort by date ascending (oldest first)
        transformed.sort(key=lambda x: x["date"])
        return transformed

    # =========================================================================
    # TECHNICAL INDICATORS CALCULATION
    # =========================================================================

    def _calculate_indicators(self, price_data: List[OHLCVData]) -> TechnicalIndicators:
        """Calculate all technical indicators needed for scoring"""

        # Get recent 90-day data for peak/low
        data_90d = price_data[-90:] if len(price_data) >= 90 else price_data

        # Peak and Low (90 days)
        peak = max(data_90d, key=lambda x: x["high"])
        low = min(data_90d, key=lambda x: x["low"])

        peak_90d = {"price": peak["high"], "date": peak["date"]}
        low_90d = {"price": low["low"], "date": low["date"]}

        # Change from peak
        change_pct = (
            (self.current_price - peak_90d["price"]) / peak_90d["price"]
        ) * 100

        return {
            "peak_90d": peak_90d,
            "low_90d": low_90d,
            "change_from_peak_pct": change_pct,
            "dma_50": self._calculate_sma(price_data, 50),
            "dma_100": self._calculate_sma(price_data, 100),
            "dma_200": self._calculate_sma(price_data, 200),
            "rsi": self._calculate_rsi(price_data, 14),
            "avg_volume_20d": self._calculate_avg_volume(price_data, 20),
            "current_volume": price_data[-1]["volume"] if price_data else 0,
            "volatility_2yr": self._calculate_volatility(price_data),
            "volatility_90d": self._calculate_volatility(data_90d),
        }

    def _calculate_sma(self, data: List[OHLCVData], period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return 0.0
        closes = [d["close"] for d in data[-period:]]
        return sum(closes) / period

    def _calculate_rsi(self, data: List[OHLCVData], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(data) < period + 1:
            return 50.0  # Neutral default

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
        annualized_vol = std_dev * (252**0.5) * 100  # 252 trading days
        return annualized_vol

    # =========================================================================
    # SCORING (Using TechnicalScore module)
    # =========================================================================

    def _calculate_all_scores(
        self, price_data: List[OHLCVData], indicators: TechnicalIndicators
    ) -> ScoreBreakdown:
        """Calculate all 6 factor scores using TechnicalScore module"""

        # Factor 1: Dip Depth
        dip_depth = score_dip_depth(abs(indicators["change_from_peak_pct"]))

        # Factor 2: Historical Context
        max_hist_dip = self._calculate_max_historical_dip(price_data)
        historical = score_historical_context(
            abs(indicators["change_from_peak_pct"]), max_hist_dip
        )

        # Factor 3: Mean Reversion
        mean_rev = score_mean_reversion(self.current_price, indicators["dma_100"])

        # Factor 4: Volatility
        volatility = score_volatility(
            indicators["volatility_90d"], indicators["volatility_2yr"]
        )

        # Factor 5: Recovery Speed
        avg_recovery, count = self._calculate_recovery_speed(price_data)
        recovery = score_recovery_speed(avg_recovery, count)

        # Factor 6: Technicals
        vol_ratio = (
            indicators["current_volume"] / indicators["avg_volume_20d"]
            if indicators["avg_volume_20d"] > 0
            else 1.0
        )
        dist_50 = (
            abs(
                (self.current_price - indicators["dma_50"]) / indicators["dma_50"] * 100
            )
            if indicators["dma_50"] > 0
            else 100
        )
        dist_100 = (
            abs(
                (self.current_price - indicators["dma_100"])
                / indicators["dma_100"]
                * 100
            )
            if indicators["dma_100"] > 0
            else 100
        )

        technicals = score_technicals(indicators["rsi"], vol_ratio, dist_50, dist_100)

        return {
            "dip_depth": dip_depth,
            "historical_context": historical,
            "mean_reversion": mean_rev,
            "volatility": volatility,
            "recovery_speed": recovery,
            "technicals": technicals,
        }

    def _calculate_max_historical_dip(self, price_data: List[OHLCVData]) -> float:
        """Calculate maximum historical dip over 2 years"""
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
    ) -> tuple[float, int]:
        """Calculate average recovery speed from significant dips (>=8%)"""
        recoveries = []

        for i in range(90, len(price_data) - 20):  # Need buffer to track recovery
            window = price_data[i - 90 : i]
            peak = max(window, key=lambda x: x["high"])["high"]
            current = price_data[i]["close"]
            dip_pct = ((peak - current) / peak) * 100

            if dip_pct >= 8:  # Significant dip threshold
                # Look for recovery (99% of peak)
                for j in range(i + 1, min(i + 91, len(price_data))):
                    if price_data[j]["close"] >= peak * 0.99:
                        recoveries.append(j - i)
                        break

        if not recoveries:
            return (60.0, 0)  # Default moderate recovery

        return (sum(recoveries) / len(recoveries), len(recoveries))


# =========================================================================
# USAGE EXAMPLE
# =========================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  ⚠️  Cannot run this file directly due to relative imports")
    print("=" * 70)
    print("\nPlease use one of these methods instead:")
    print("\n1. Use the standalone runner:")
    print("   python src/stocks/run_analysis.py")
    print("\n2. Run as a module:")
    print("   cd src && python -m stocks.TechnicalAnalysis")
    print("\n3. Import and use in your own script:")
    print("   from stocks import TechnicalAnalysis")
    print("   analyzer = TechnicalAnalysis(...)")
    print("   result = analyzer.analyze()")
    print("\n" + "=" * 70 + "\n")
