# data_processors/report_generators.py
from dataclasses import dataclass
from typing import Dict, List, Any
import pandas as pd
from config import Config
import numpy as np

@dataclass
class ReportConfig:
    """Configuration for report generation"""
    DAYS_OF_WEEK = Config.DAYS_OF_WEEK
    CATEGORIES = Config.CATEGORIES
    LEVELS = Config.LEVELS

def convert_to_serializable(obj: Any) -> Any:
    """Convert numpy/pandas numeric types to Python native types"""
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    return obj


class SummaryTableGenerator:
    """Generates the summary table with daily breakdowns"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()  # Create a copy to avoid modifying original
        # Fill any NA values in level with 'Unknown'
        self.df['level'] = self.df['level'].fillna('Unknown')
        
    def _initialize_summary(self) -> Dict[str, Dict[str, int]]:
        """Initialize the summary dictionary with all possible combinations"""
        summary = {}
        
        # Initialize all level-specific run counts
        for level in ReportConfig.LEVELS:
            summary[f'{level} Ran'] = {day: 0 for day in ReportConfig.DAYS_OF_WEEK}
            summary[f'{level} Ran']['Total'] = 0
            
        # Initialize other metrics
        other_metrics = ['Total Ran', 'Turned', 'Cancelled', 'Total Missed', 'Total Demand']
        for metric in other_metrics:
            summary[metric] = {day: 0 for day in ReportConfig.DAYS_OF_WEEK}
            summary[metric]['Total'] = 0
            
        return summary
        
    def generate(self) -> Dict[str, Dict[str, Any]]:
        """Generate summary table with daily counts by type"""
        # Initialize summary with all possible combinations
        summary = self._initialize_summary()
        
        # Process each row
        for _, row in self.df.iterrows():
            day = row['weekday']
            category = row['category']
            level = row['level']
            
            if category == 'Ran' and level in ReportConfig.LEVELS:
                # Update level-specific count
                summary[f'{level} Ran'][day] += 1
                summary[f'{level} Ran']['Total'] += 1
                # Update total runs
                summary['Total Ran'][day] += 1
                summary['Total Ran']['Total'] += 1
            elif category == 'Turned':
                summary['Turned'][day] += 1
                summary['Turned']['Total'] += 1
                summary['Total Missed'][day] += 1
                summary['Total Missed']['Total'] += 1
            elif category == 'Cancelled':
                summary['Cancelled'][day] += 1
                summary['Cancelled']['Total'] += 1
                summary['Total Missed'][day] += 1
                summary['Total Missed']['Total'] += 1
            
            # Update total demand
            if category in ReportConfig.CATEGORIES:
                summary['Total Demand'][day] += 1
                summary['Total Demand']['Total'] += 1
            
        return convert_to_serializable(summary)

class OriginReportGenerator:
    """Generates the origin report including full report and top 5 lists"""
    
    def __init__(self, current_df: pd.DataFrame, previous_df: pd.DataFrame):
        self.current_df = current_df
        self.previous_df = previous_df
        
    def _get_delta_format(self, current: int, previous: int) -> str:
        """Format delta with color coding for latex"""
        delta = current - previous
        if delta == 0:
            return "0"
        color = "green" if delta > 0 else "red"
        sign = "+" if delta > 0 else ""
        return f"\\textcolor{{{color}}}{{\\textbf{{{sign}{delta}}}}}"
    
    def generate_full_report(self) -> List[Dict[str, Any]]:
        """Generate full report for all origins"""
        # Group current week's data
        current_grouped = self.current_df[self.current_df['category'] == 'Ran'].groupby('origin').agg({
            'level': lambda x: list(x)
        }).reset_index()
        
        # Group previous week's data
        prev_grouped = self.previous_df[self.previous_df['category'] == 'Ran'].groupby('origin').size().reset_index(
            name='PrevTotal'
        )
        
        report = []
        for _, row in current_grouped.iterrows():
            levels = row['level']
            als_count = levels.count('ALS')
            bls_count = levels.count('BLS')
            ccu_count = levels.count('CCU')
            total = len(levels)
            
            prev_total = prev_grouped[prev_grouped['origin'] == row['origin']]['PrevTotal'].iloc[0] if len(
                prev_grouped[prev_grouped['origin'] == row['origin']]) > 0 else 0
            
            report.append({
                'origin': row['origin'],
                'ALS': als_count,
                'BLS': bls_count,
                'CCU': ccu_count,
                'Total': total,
                'PrevTotal': prev_total,
                'Delta': self._get_delta_format(total, prev_total)
            })
            
        # Add total row
        total_row = {
            'origin': 'TOTAL',
            'ALS': sum(r['ALS'] for r in report),
            'BLS': sum(r['BLS'] for r in report),
            'CCU': sum(r['CCU'] for r in report),
            'Total': sum(r['Total'] for r in report),
            'PrevTotal': sum(r['PrevTotal'] for r in report),
            'Delta': self._get_delta_format(
                sum(r['Total'] for r in report),
                sum(r['PrevTotal'] for r in report)
            )
        }
        
        # Add separator and total
        report.append({'origin': '\\hline', 'ALS': 0, 'BLS': 0, 'CCU': 0, 'Total': 0, 'PrevTotal': 0, 'Delta': 0})
        report.append(total_row)
        
        return convert_to_serializable(report)
    
    def generate_top_5_lists(self) -> Dict[str, List[Dict[str, int]]]:
        """Generate top 5 lists for each level and total"""
        current_ran = self.current_df[self.current_df['category'] == 'Ran']
        
        # Get counts by origin and level
        level_counts = current_ran.groupby(['origin', 'level']).size().unstack(fill_value=0)
        total_counts = current_ran.groupby('origin').size()
        
        # Create top 5 lists
        top_5_als = (level_counts['ALS'] if 'ALS' in level_counts.columns else pd.Series()).nlargest(5)
        top_5_bls = (level_counts['BLS'] if 'BLS' in level_counts.columns else pd.Series()).nlargest(5)
        top_5_ccu = (level_counts['CCU'] if 'CCU' in level_counts.columns else pd.Series()).nlargest(5)
        top_5_total = total_counts.nlargest(5)
        
        return {
            'top_5_als': [{'origin': origin, 'ALS': count} for origin, count in top_5_als.items()],
            'top_5_bls': [{'origin': origin, 'BLS': count} for origin, count in top_5_bls.items()],
            'top_5_ccu': [{'origin': origin, 'CCU': count} for origin, count in top_5_ccu.items()],
            'top_5_total': [{'origin': origin, 'Total': count} for origin, count in top_5_total.items()]
        }

class MemphisSpecializedReportGenerator:
    """Generates Memphis-specific hospital system reports"""
    
    def __init__(self, current_df: pd.DataFrame, previous_df: pd.DataFrame):
        self.current_df = current_df
        self.previous_df = previous_df
        self.origin_report_gen = OriginReportGenerator(current_df, previous_df)
        
    def generate(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate specialized reports for Methodist, Baptist, and St Francis"""
        full_report = self.origin_report_gen.generate_full_report()
        
        def filter_hospitals(name_pattern: str) -> List[Dict[str, Any]]:
            hospitals = [row for row in full_report if name_pattern in row['origin']]
            if not hospitals:
                return []
                
            total_row = {
                'origin': 'TOTAL',
                'ALS': sum(h['ALS'] for h in hospitals),
                'BLS': sum(h['BLS'] for h in hospitals),
                'CCU': sum(h['CCU'] for h in hospitals),
                'Total': sum(h['Total'] for h in hospitals),
                'PrevTotal': sum(h['PrevTotal'] for h in hospitals),
                'Delta': self.origin_report_gen._get_delta_format(
                    sum(h['Total'] for h in hospitals),
                    sum(h['PrevTotal'] for h in hospitals)
                )
            }
            
            return hospitals + [
                {'origin': '\\hline', 'ALS': '', 'BLS': '', 'CCU': '', 'Total': '', 'PrevTotal': '', 'Delta': ''},
                total_row
            ]
        
        return {
            'methodist_table': filter_hospitals('METHODIST HOSPITAL'),
            'baptist_table': filter_hospitals('BAPTIST MEMORIAL HOSPITAL'),
            'st_francis_table': filter_hospitals('ST FRANCIS HOSPITAL')
        }