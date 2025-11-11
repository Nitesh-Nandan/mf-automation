"""
Custom Exceptions for Mutual Fund Analyzer

Provides specific exception types for better error handling and debugging.
"""


class MFAnalyzerError(Exception):
    """Base exception for all MF Analyzer errors"""

    pass


class DataFetchError(MFAnalyzerError):
    """Raised when data fetching from API fails"""

    def __init__(self, code: str, message: str = "Failed to fetch data"):
        self.code = code
        self.message = f"{message} for fund code: {code}"
        super().__init__(self.message)


class InsufficientDataError(MFAnalyzerError):
    """Raised when there's not enough data for analysis"""

    def __init__(self, fund_name: str, required_days: int, available_days: int):
        self.fund_name = fund_name
        self.required_days = required_days
        self.available_days = available_days
        self.message = (
            f"Insufficient data for {fund_name}: "
            f"Required {required_days} days, but only {available_days} available"
        )
        super().__init__(self.message)


class ConfigurationError(MFAnalyzerError):
    """Raised when configuration is invalid"""

    def __init__(self, parameter: str, message: str):
        self.parameter = parameter
        self.message = f"Configuration error for '{parameter}': {message}"
        super().__init__(self.message)


class FundNotFoundError(MFAnalyzerError):
    """Raised when a fund is not found in the portfolio"""

    def __init__(self, fund_identifier: str):
        self.fund_identifier = fund_identifier
        self.message = f"Fund not found: {fund_identifier}"
        super().__init__(self.message)


class InvalidModeError(MFAnalyzerError):
    """Raised when an invalid analysis mode is provided"""

    def __init__(self, mode: str, valid_modes: list[str]):
        self.mode = mode
        self.valid_modes = valid_modes
        self.message = (
            f"Invalid mode '{mode}'. " f"Valid modes are: {', '.join(valid_modes)}"
        )
        super().__init__(self.message)
