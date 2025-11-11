"""
Constants for Mutual Fund Analyzer

Centralized constants to avoid magic strings and numbers throughout the codebase.
"""

# Date formats
DATE_FORMAT_API = "%d-%m-%Y"  # Format used by API: 03-03-2025
DATE_FORMAT_SHORT = "%d-%b-%y"  # Short format: 03-Mar-25
DATE_FORMAT_FULL = "%d %B %Y"  # Full format: 03 March 2025
DATE_FORMAT_ISO = "%Y-%m-%d"  # ISO format: 2025-03-03

# Display settings
SEPARATOR_LINE = "=" * 80
SEPARATOR_SHORT = "-" * 80
SEPARATOR_MINI = "-" * 70

# Emoji indicators (for console output)
EMOJI_ROCKET = "🚀"
EMOJI_TARGET = "🎯"
EMOJI_CHART = "📊"
EMOJI_UP = "📈"
EMOJI_DOWN = "📉"
EMOJI_CHECK = "✅"
EMOJI_CROSS = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_STAR = "⭐"
EMOJI_FIRE = "🔥"
EMOJI_BRAIN = "🧠"
EMOJI_MONEY = "💰"
EMOJI_EMAIL = "📧"
EMOJI_SEARCH = "🔍"
EMOJI_BULB = "💡"

# Fund types
FUND_TYPE_SMALL_CAP = "Small Cap"
FUND_TYPE_MID_CAP = "Mid Cap"
FUND_TYPE_LARGE_CAP = "Large Cap"
FUND_TYPE_FLEXI_CAP = "Flexi Cap"
FUND_TYPE_SECTORAL = "Sectoral"
FUND_TYPE_THEMATIC = "Thematic"
FUND_TYPE_DEBT = "Debt/Liquid"

# Recommendation levels
REC_STRONG_BUY = "STRONG BUY"
REC_BUY = "BUY"
REC_MODERATE_BUY = "MODERATE BUY"
REC_WEAK_BUY = "WEAK BUY"
REC_HOLD = "HOLD"

# Confidence levels
CONFIDENCE_VERY_HIGH = "Very High"
CONFIDENCE_HIGH = "High"
CONFIDENCE_MEDIUM = "Medium"
CONFIDENCE_LOW = "Low"
CONFIDENCE_NONE = "None"

# Analysis modes
MODE_ULTRA_CONSERVATIVE = "ultra_conservative"
MODE_CONSERVATIVE = "conservative"
MODE_MODERATE = "moderate"
MODE_AGGRESSIVE = "aggressive"

# Factor names (for scoring)
FACTOR_DIP_DEPTH = "Dip Depth"
FACTOR_HISTORICAL_CONTEXT = "Historical Context"
FACTOR_MEAN_REVERSION = "Mean Reversion"
FACTOR_VOLATILITY = "Volatility"
FACTOR_RECOVERY_SPEED = "Recovery Speed"
FACTOR_FUND_CATEGORY = "Fund Category"

# Score limits
SCORE_MIN = 0
SCORE_MAX = 100

# Maximum score per factor
MAX_SCORE_DIP_DEPTH = 40
MAX_SCORE_HISTORICAL_CONTEXT = 13
MAX_SCORE_MEAN_REVERSION = 13
MAX_SCORE_VOLATILITY = 11
MAX_SCORE_RECOVERY_SPEED = 13
MAX_SCORE_FUND_CATEGORY = 10

# Position sizing
DEFAULT_MIN_INVESTMENT = 5000  # ₹5,000
DEFAULT_MAX_PER_FUND = 0.30  # 30%
DEFAULT_RESERVE = 0.20  # 20%

# Display widths (for table formatting)
WIDTH_FUND_NAME = 40
WIDTH_SCORE = 8
WIDTH_DIP = 8
WIDTH_RECOMMENDATION = 15
WIDTH_ALLOCATION = 8

# Error messages
ERROR_NO_DATA = "No data available"
ERROR_INSUFFICIENT_DATA = "Insufficient data for analysis"
ERROR_INVALID_MODE = "Invalid analysis mode"
ERROR_API_FAILURE = "API request failed"
ERROR_NO_CODE = "No API code provided"

# CSV column names
CSV_FUND_NAME = "fund_name"
CSV_TYPE = "type"
CSV_CODE = "code"
CSV_URL = "url"

# Trading days per year (for volatility calculation)
TRADING_DAYS_PER_YEAR = 252

# API settings
API_TIMEOUT_SECONDS = 10
API_RETRY_COUNT = 3

# File names
FUND_CSV_FILENAME = "mf_funds.csv"
