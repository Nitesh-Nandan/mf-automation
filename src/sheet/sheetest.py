import logging

from google_sheet import SpreadSheet

logging.basicConfig(level=logging.INFO)


def get_spreadsheet():
    google_sheets = SpreadSheet(
        sheetUrl="https://docs.google.com/spreadsheets/d/1uch8IQq3jJ_3QcYcm2LzPzYjb4zfVjX_ckoqjstVb0E"
    )

    worksheet = google_sheets.get_worksheet("Emerging")
    data = worksheet.get_all_records()
    print(data)


if __name__ == "__main__":
    get_spreadsheet()
