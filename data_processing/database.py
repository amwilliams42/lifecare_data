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

    def fetch_data_for_period(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch data for a specific date range.
        
        Args:
            start_date: Start date in MM/DD/YYYY format
            end_date: End date in MM/DD/YYYY format
            
        Returns:
            DataFrame containing the requested data
        """
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
                    params=(start_date, end_date)
                )
                
                # Convert date_of_service to datetime, handling any invalid dates
                df['date_of_service'] = pd.to_datetime(
                    df['date_of_service'], 
                    format=Config.DB_DATE_FORMAT,
                    errors='coerce'  # Convert invalid dates to NaT
                )
                
                # Remove any rows with invalid dates
                df = df.dropna(subset=['date_of_service'])
                
            print(df.head())    
            return df
                    
        except Exception as e:
            raise Exception(f"Data fetch error: {str(e)}")