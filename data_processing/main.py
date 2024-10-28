import json
import os
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from report_manager import WeeklyReportManager
from transport_processor import TransportDataProcessor
from config import Config

class Logger:
    """Simple logging class for report generation"""
    
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        self.date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Setup log files
        self.daily_log = self.output_dir / f"report_log_{self.date_str}.txt"
        self.error_log = self.output_dir / "error_log.txt"
        
    def log_message(self, message: str, is_error: bool = False, include_trace: bool = False):
        """Log a message with timestamp and optional stack trace"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        if is_error and include_trace:
            log_message += f"Stack trace:\n{traceback.format_exc()}\n"
        
        # Write to daily log
        with open(self.daily_log, 'a') as f:
            f.write(log_message)
            
        # If error, also write to error log
        if is_error:
            with open(self.error_log, 'a') as f:
                f.write(log_message)
            # Also print to stderr for immediate visibility
            print(log_message, file=sys.stderr)


def validate_date_format(date_str: str) -> bool:
    """Validate that date string matches required format"""
    try:
        datetime.strptime(date_str, '%m/%d/%Y')
        return True
    except ValueError:
        return False

def generate_report(start_date: str, end_date: str, logger: Logger) -> None:
    """Generate weekly report and save to files"""
    try:
        # Log start of report generation
        logger.log_message(f"Starting report generation for period: {start_date} to {end_date}")
        
        # Initialize data processor and load data
        logger.log_message("Loading data from database...")
        processor = TransportDataProcessor()
        processor.load_data(start_date, end_date)
        
        # Generate report
        logger.log_message("Generating report...")
        report_manager = WeeklyReportManager(
            processor.current_week_data,
            processor.previous_week_data
        )
        report_data = report_manager.generate_complete_report()
        
        # Generate output filename and save JSON report
        filename = f"report_{start_date.replace('/', '-')}_{end_date.replace('/', '-')}.json"
        output_path = Config.OUTPUT_DIR / filename
        
        logger.log_message(f"Saving report to {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
            
        logger.log_message("Report generated successfully")
        
    except Exception as e:
        error_msg = f"Error generating report: {str(e)}"
        logger.log_message(error_msg, is_error=True, include_trace=True)
        sys.exit(1)

def main():
    """Main entry point for report generation"""
    try:
        # Check command line arguments
        if len(sys.argv) != 3:
            raise ValueError("Incorrect number of arguments. Usage: python main.py <start_date> <end_date>")
            
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        
        # Setup logger
        logger = Logger()
        
        # Generate report
        generate_report(start_date, end_date, logger)
        
    except Exception as e:
        # If we can't even set up logging, just print to stderr
        error_msg = f"Critical error: {str(e)}"
        print(f"{error_msg}\n{traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()