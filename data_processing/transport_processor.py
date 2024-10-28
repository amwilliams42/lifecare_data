from database import DatabaseManager
from date_utils import DateManager
from config import Config

class TransportDataProcessor:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.current_week_data = None
        self.previous_week_data = None
        
    def load_data(self, start_date: str, end_date: str):
        """Load data for current and previous weeks."""
        date_ranges = DateManager.get_date_ranges(start_date, end_date)
        
        self.current_week_data = self.db_manager.fetch_data_for_period(
            *date_ranges['current']
        )
        self.previous_week_data = self.db_manager.fetch_data_for_period(
            *date_ranges['previous']
        )
    
    def get_basic_summary(self) -> dict:
        """Generate basic summary of loaded data."""
        if self.current_week_data is None or self.previous_week_data is None:
            raise Exception("No data loaded. Please run load_data first.")
        
        return {
            "current_week": {
                "date_range": {
                    "start": self.current_week_data['date_of_service'].min().strftime(Config.DATE_FORMAT),
                    "end": self.current_week_data['date_of_service'].max().strftime(Config.DATE_FORMAT)
                },
                "total_records": len(self.current_week_data),
                "divisions": self.current_week_data['division'].unique().tolist()
            },
            "previous_week": {
                "date_range": {
                    "start": self.previous_week_data['date_of_service'].min().strftime(Config.DATE_FORMAT),
                    "end": self.previous_week_data['date_of_service'].max().strftime(Config.DATE_FORMAT)
                },
                "total_records": len(self.previous_week_data),
                "divisions": self.previous_week_data['division'].unique().tolist()
            }
        }
