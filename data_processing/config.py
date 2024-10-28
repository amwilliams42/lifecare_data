from pathlib import Path


class Config:
    DATABASE_PATH = "../data.db"
    DATE_FORMAT = "%m/%d/%Y"
    DB_DATE_FORMAT = "%m/%d/%y"
    DIVISIONS = ["Memphis", "Nashville"]
    PRIORITIES = ["Emergent", "Non Emergent"]
    CATEGORIES = ["Cancelled", "Ran", "Turned"]
    LEVELS = ["ALS", "BLS", "CCU"]
    DAYS_OF_WEEK = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    OUTPUT_DIR = Path(__file__).parent.parent / 'tmp_output'


    @classmethod
    def setup_output_directory(cls) -> Path:
        """Create and return output directory"""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return cls.OUTPUT_DIR