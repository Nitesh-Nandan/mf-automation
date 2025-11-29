import logging
import gspread
from typing import List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

class SpreadSheet:
    """
    A client for interacting with a specific Google Spreadsheet.
    """
    
    def __init__(self, sheetUrl: str, credentials_path: Union[str, Path] = "service_account.json"):
        """
        Initialize, authenticate, and open the spreadsheet.
        """
        self.credentials_path = Path(credentials_path)
        self.client = None
        self.spreadsheet = None
        
        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")
            
        try:
            self.client = gspread.service_account(filename=str(self.credentials_path))
            logger.info(f"✅ Authenticated using {self.credentials_path.name}")
            
            if sheetUrl.startswith("https://"):
                self.spreadsheet = self.client.open_by_url(sheetUrl)
            else:
                self.spreadsheet = self.client.open_by_key(sheetUrl)
            logger.info(f"✅ Opened spreadsheet: {self.spreadsheet.title}")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise

    def get_all_worksheets(self) -> List[gspread.Worksheet]:
        """
        Get all worksheets from the spreadsheet.
        """
        if not self.spreadsheet:
             raise RuntimeError("Spreadsheet not initialized")
        return self.spreadsheet.worksheets()

    def get_worksheet(self, worksheet_name: str) -> gspread.Worksheet:
        """
        Get a specific worksheet by name.
        """
        if not self.spreadsheet:
             raise RuntimeError("Spreadsheet not initialized")
        try:
            return self.spreadsheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            logger.error(f"❌ Worksheet '{worksheet_name}' not found.")
            raise
