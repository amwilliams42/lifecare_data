# data_processors/report_manager.py
from typing import Dict, Any
from pathlib import Path
from datetime import datetime
import pandas as pd
from graph_generator import ReportGraphManager
from report_generator import (
    SummaryTableGenerator,
    OriginReportGenerator,
    MemphisSpecializedReportGenerator
)
from config import Config

class WeeklyReportManager:
    """Manages the generation of the complete weekly report"""
    
    def __init__(self, current_week_data: pd.DataFrame, previous_week_data: pd.DataFrame):
        self.current_week_data = current_week_data
        self.previous_week_data = previous_week_data
        self.ouput_dir = Config.OUTPUT_DIR
        
    def generate_division_report(self, division: str) -> Dict[str, Any]:
        """Generate complete report for a division"""
        # Filter data for division
        current_div_data = self.current_week_data[self.current_week_data['division'] == division]
        previous_div_data = self.previous_week_data[self.previous_week_data['division'] == division]
        
        # Get date range
        start_date = current_div_data['date_of_service'].min().strftime('%m/%d/%Y')
        end_date = current_div_data['date_of_service'].max().strftime('%m/%d/%Y')
        
        # Initialize report generators
        summary_gen = SummaryTableGenerator(current_div_data)
        origin_gen = OriginReportGenerator(current_div_data, previous_div_data)
        graph_gen = ReportGraphManager()
        
        # Build basic report structure
        report = {
            'division': division,
            'start_date': start_date,
            'end_date': end_date,
            'total_records': len(current_div_data),
            'summary_table': summary_gen.generate(),
            'origin_report': {
                'full_report': origin_gen.generate_full_report(),
                **origin_gen.generate_top_5_lists()
            },
        }

        graph_paths = graph_gen.generate_division_graphs(
            current_div_data,
            division,
            start_date,
            end_date
        )

        report.update(graph_paths)
        
        # Add Memphis-specific report if applicable
        if division == 'Memphis':
            memphis_gen = MemphisSpecializedReportGenerator(current_div_data, previous_div_data)
            report['memphis_specialized_report'] = memphis_gen.generate()
        
        return report
    
    def generate_complete_report(self) -> Dict[str, Dict[str, Any]]:
        """Generate complete report for all divisions"""
        return {
            division: self.generate_division_report(division)
            for division in ['Memphis', 'Nashville']
        }