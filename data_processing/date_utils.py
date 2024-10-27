from datetime import datetime, timedelta
from config import Config

class DateManager:
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Convert date string to datetime object."""
        return datetime.strptime(date_str, Config.DATE_FORMAT)
    
    @staticmethod
    def format_date(dt: datetime) -> str:
        """Convert datetime object to string."""
        return dt.strftime(Config.DATE_FORMAT)
    
    @staticmethod
    def get_date_ranges(start_date: str, end_date: str) -> dict:
        """
        Calculate current and previous week date ranges.
        
        Returns:
            dict containing current and previous week date ranges
        """
        start_dt = DateManager.parse_date(start_date)
        end_dt = DateManager.parse_date(end_date)
        
        prev_start = start_dt - timedelta(days=7)
        prev_end = end_dt - timedelta(days=7)
        
        return {
            'current': (start_date, end_date),
            'previous': (
                DateManager.format_date(prev_start),
                DateManager.format_date(prev_end)
            )
        }