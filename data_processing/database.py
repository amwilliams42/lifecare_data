import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from config import Config

class DatabaseManager:
    def __init__(self, db_path=Config.DATABASE_PATH):
        self.db_path = db_path

    def get_connection(self):
        """Create and return a database connection."""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            raise Exception(f"Database connection error: {str(e)}")

    def _convert_date_format(self, date_str: str) -> str:
        """Convert from MM/DD/YYYY to MM/DD/YY format for database queries."""
        try:
            dt = datetime.strptime(date_str, Config.DATE_FORMAT)
            return dt.strftime(Config.DB_DATE_FORMAT)
        except ValueError as e:
            raise Exception(f"Date conversion error: {str(e)}")

    def fetch_data_for_period(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch data for a specific date range.
        
        Args:
            start_date: Start date in MM/DD/YYYY format
            end_date: End date in MM/DD/YYYY format
            
        Returns:
            DataFrame containing the requested data
        """
        # Convert input dates to database format (MM/DD/YY)
        db_start_date = self._convert_date_format(start_date)
        db_end_date = self._convert_date_format(end_date)
        
        query = """
        SELECT 
            date_of_service,
            division,
            priority,
            category,
            level,
            weekday,
            Hour,
            origin,
            response_time
        FROM records
        WHERE date_of_service BETWEEN ? AND ?
        """
        
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(
                    query,
                    conn,
                    params=(db_start_date, db_end_date)
                )
                
                # Convert two-digit years to four-digit years
                df['date_of_service'] = pd.to_datetime(
                    df['date_of_service'],
                    format=Config.DB_DATE_FORMAT
                )
                
                return df
                
        except Exception as e:
            raise Exception(f"Data fetch error: {str(e)}")
