import logging
from typing import Optional
from dataclasses import dataclass, field

import pandas as pd

from googleapiclient.discovery import build
from google.oauth2 import service_account


@dataclass
class GoogleSheetsReader:
    """
    A class to read data from a Google Sheets document.

    Attributes:
        credentials_file (str): Path to the Google service account credentials file.
        spreadsheet_id (str): The ID of the Google Sheets document.
        sheet_range (str): The range of cells to read (e.g., 'Sheet1!A1:D100').
        spreadsheet_service (Optional[object]): Google Sheets API service instance.
        data (Optional[pd.DataFrame]): DataFrame containing the retrieved sheet data.
    """

    credentials_file: str
    spreadsheet_id: str
    sheet_range: str
    spreadsheet_service: Optional[object] = field(init=False, default=None, repr=False)
    data: Optional[pd.DataFrame] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """
        Initialize the Google Sheets API service after dataclass initialization.

        Raises:
            Exception: If authorization fails.
        """
        try:
            # Authorize Google Sheets API service
            self.spreadsheet_service = self._authorize()
            logging.info("Authorization successful.")
            # Retrieve data from Google Sheets
            self.data = self._get_data()
        except Exception as e:
            logging.error(f"Failed to authorize Google Sheets API: {e}")
            raise

    def _authorize(self) -> object:
        """
        Authorize the Google Sheets API with service account credentials.

        Returns:
            object: The Google Sheets API service instance.

        Raises:
            Exception: If credentials file is not found or invalid.
        """
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        try:
            # Load credentials from the specified file
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            logging.info("Credentials successfully loaded.")
            # Build the service for Google Sheets API
            return build("sheets", "v4", credentials=creds)
        except Exception as e:
            logging.error(f"Failed to load credentials: {e}")
            raise

    def _get_data(self) -> pd.DataFrame:
        """
        Retrieve raw data from Google Sheets and return it as a DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing the retrieved data.

        Raises:
            Exception: If there is an issue with data retrieval.
        """
        try:
            if self.spreadsheet_service is None:
                # Ensure authorization if not already done
                self.spreadsheet_service = self._authorize()

            # Access the specified sheet and range
            sheet = self.spreadsheet_service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=self.spreadsheet_id, range=self.sheet_range)
                .execute()
            )
            values = result.get("values", [])

            if not values:
                logging.warning("No data found in the specified range.")
                return pd.DataFrame()  # Return an empty DataFrame if no data is found

            # Convert the retrieved values into a DataFrame
            df = pd.DataFrame(values[1:], columns=values[0])
            logging.info("Data successfully retrieved from Google Sheets.")
            return df
        except Exception as e:
            logging.error(f"Failed to retrieve data from Google Sheets: {e}")
            return pd.DataFrame()  # Return an empty DataFrame on error
