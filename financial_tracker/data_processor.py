import logging
from dataclasses import dataclass, field

import pandas as pd

from financial_tracker.data_reader import GoogleSheetsReader


@dataclass
class DataProcessor:
    """
    A class to process financial data retrieved from Google Sheets.

    Attributes:
        sheets_reader (GoogleSheetsReader): An instance of GoogleSheetsReader for data retrieval.
        data (pd.DataFrame): The processed data from Google Sheets.
    """

    sheets_reader: GoogleSheetsReader
    data: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the DataProcessor by retrieving data from GoogleSheetsReader
        and performing initial data processing.

        Raises:
            ValueError: If sheets_reader is not an instance of GoogleSheetsReader.
        """
        if not isinstance(self.sheets_reader, GoogleSheetsReader):
            logging.error("Provided data must be an instance of GoogleSheetsReader.")
            raise ValueError("Invalid data type. Must be GoogleSheetsReader.")

        self.data = self.sheets_reader.data
        self._check_and_convert_data_types()
        self._replace_nan()

    def _check_and_convert_data_types(self) -> None:
        """
        Ensure that the 'date' column is in datetime format and numeric columns are
        properly converted to numeric types.
        """
        # Convert 'date' column to datetime format
        if "date" in self.data.columns:
            self.data["date"] = pd.to_datetime(self.data["date"], errors="coerce")

        # Define numeric columns for conversion
        numeric_cols = ["sum rub", "sum currency"]
        for col in numeric_cols:
            if col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors="coerce")

        logging.info("Data types checked and converted where necessary.")

    def _replace_nan(self) -> None:
        """
        Replace NaN values with zero in the DataFrame.
        """
        self.data.fillna(0, inplace=True)
        logging.info("NaN values replaced with zeros in the DataFrame.")

    def set_index(self, column_name: str) -> None:
        """
        Set the specified column as the index of the DataFrame.

        Args:
            column_name (str): The name of the column to set as index.

        Raises:
            ValueError: If the specified column does not exist in the DataFrame.
        """
        if column_name in self.data.columns:
            self.data.set_index(column_name, inplace=True)
            logging.info(f"Column '{column_name}' set as index.")
        else:
            logging.error(f"Column '{column_name}' not found in DataFrame.")
            raise ValueError(f"Column '{column_name}' not found in DataFrame.")

    def filter_by_category(self, category: str) -> pd.DataFrame:
        """
        Filter the data by a specific category.

        Args:
            category (str): The category to filter by.

        Returns:
            pd.DataFrame: Filtered DataFrame with the specified category.
        """
        return self.data[self.data["category"] == category]

    def filter_by_period(self, period: str) -> pd.DataFrame:
        """
        Filter the data by a specific period.

        Args:
            period (str): The period to filter by.

        Returns:
            pd.DataFrame: Filtered DataFrame for the specified period.
        """
        return self.data[self.data["period"] == period]

    def get_category_summary(self) -> pd.DataFrame:
        """
        Get aggregated data by category.

        Returns:
            pd.DataFrame: DataFrame with total sum by category.
        """
        return self.data.groupby("category")["sum rub"].sum().reset_index()

    def get_subcategory_summary(self, category: str) -> pd.DataFrame:
        """
        Get aggregated data by subcategory for a specific category.

        Args:
            category (str): The category to summarize by subcategory.

        Returns:
            pd.DataFrame: DataFrame with total sum by subcategory.
        """
        filtered_data = self.filter_by_category(category)
        return filtered_data.groupby("subcategory")["sum rub"].sum().reset_index()

    def get_monthly_summary(self) -> pd.DataFrame:
        """
        Get aggregated monthly data.

        Returns:
            pd.DataFrame: DataFrame with total sum per month.
        """
        self.data["month"] = pd.to_datetime(self.data["date"]).dt.to_period("M")
        monthly_totals = self.data.groupby("month")["sum rub"].sum().reset_index()
        monthly_totals["month"] = monthly_totals["month"].dt.strftime("%Y-%m")
        return monthly_totals

    def get_category_mean_median(self) -> pd.DataFrame:
        """
        Calculate the mean and median expenses for each category.

        Returns:
            pd.DataFrame: DataFrame with category, mean, and median expenses.
        """
        try:
            summary = (
                self.data.groupby("category")["sum rub"]
                .agg(["mean", "median"])
                .reset_index()
            )
            summary.columns = ["category", "mean_expense", "median_expense"]
            logging.info("Calculated mean and median expenses by category.")
            return summary
        except Exception as e:
            logging.error(f"Failed to calculate mean and median expenses: {e}")
            return pd.DataFrame()
