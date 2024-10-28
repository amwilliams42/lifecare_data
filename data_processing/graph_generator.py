from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from pathlib import Path
import pandas as pd
from config import Config
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

@dataclass
class GraphConfig:
    """Configuration for graph generation"""
    DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    DAY_MAP = {
        'Monday': 'Mon', 
        'Tuesday': 'Tue', 
        'Wednesday': 'Wed', 
        'Thursday': 'Thu', 
        'Friday': 'Fri', 
        'Saturday': 'Sat', 
        'Sunday': 'Sun'
    }
    RESPONSE_TIME_MAX = 1440  # 24 hours in minutes
    HEATMAP_FIGSIZE = (16, 8)
    RESPONSE_TIME_FIGSIZE = (12, 6)

class GraphGenerator:
    """Base class for generating graphs"""
    
    def __init__(self):
        plt.style.use('default')  # Set consistent style
        sns.set_theme(style="whitegrid")
    
    def _save_plot(self, filename: str) -> str:
        """Save plot to file and return path"""
        filepath = Config.OUTPUT_DIR / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        return str(filepath)

class HeatmapGenerator(GraphGenerator):
    """Generates heatmaps for different call categories"""
    
    def _prepare_data(self, df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
        """Prepare dataframe for heatmap generation"""
        # Convert dates and filter
        date_range = pd.date_range(start=start_date, end=end_date)
        df = df[df['date_of_service'].dt.date.isin(date_range.date)]
        
        # Map days to shortened versions
        df['day_of_week'] = df['date_of_service'].dt.day_name().map(GraphConfig.DAY_MAP)
        
        # Add count column for aggregation
        df['count'] = 1
        
        return df
    
    def _create_heatmap(
        self, 
        data: pd.DataFrame, 
        title: str, 
        division: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Create and configure a heatmap"""
        plt.figure(figsize=GraphConfig.HEATMAP_FIGSIZE)
        
        # Create pivot table using count column instead of id
        pivot = pd.pivot_table(
            data,
            values='count',  # Changed from 'id' to 'count'
            index='day_of_week',
            columns='hour',
            aggfunc='sum',  # Changed from 'count' to 'sum'
            fill_value=0
        )
        
        # Ensure all hours are present and reindex days
        pivot = pivot.reindex(
            index=GraphConfig.DAYS_OF_WEEK,
            columns=range(24),
            fill_value=0
        )
        
        # Create heatmap
        sns.heatmap(
            pivot,
            cmap="YlOrRd",
            annot=True,
            fmt="d",
            cbar_kws={'label': 'Number of Calls'}
        )
        
        plt.title(f'{title} - {division}\n{start_date} to {end_date}')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.xticks(range(0, 24, 1), range(24))
        plt.tight_layout()
        
        return pivot
    
    def generate_heatmaps(
        self,
        df: pd.DataFrame,
        division: str,
        start_date: str,
        end_date: str
    ) -> Tuple[str, str, str]:
        """Generate all heatmaps for a division"""
        
        # Prepare data
        df = self._prepare_data(df, start_date, end_date)
        
        # Generate heatmaps for each category
        categories = {
            'Turned': 'Turned Calls by Hour and Day',
            'Cancelled': 'Cancelled Calls by Hour and Day',
            'Ran': 'Ran Calls by Hour and Day'
        }
        
        paths = []
        for category, title in categories.items():
            category_data = df[df['category'] == category]
            pivot = self._create_heatmap(category_data, title, division, start_date, end_date)
            
            filename = f'{category.lower()}_heatmap_{division}_{start_date.replace("/", "-")}_{end_date.replace("/", "-")}.png'
            paths.append(self._save_plot(filename))
        
        return tuple(paths)

class ResponseTimeDistributionGenerator(GraphGenerator):
    """Generates response time distribution graphs"""
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for response time distribution"""
        # Convert response_time to numeric and clean data
        df = df.copy()
        df['response_time'] = pd.to_numeric(df['response_time'], errors='coerce')
        
        # Remove invalid values and outliers
        df = df.dropna(subset=['response_time', 'priority'])
        df = df[
            (df['response_time'] <= GraphConfig.RESPONSE_TIME_MAX) &
            (df['response_time'] > 0)
        ]
        
        return df
    
    def generate_distribution(
        self,
        df: pd.DataFrame,
        division: str,
        start_date: str,
        end_date: str
    ) -> Optional[str]:
        """Generate response time distribution graph"""
        # Prepare data
        df = self._prepare_data(df)
        
        if df.empty:
            return None
        
        # Create plot
        plt.figure(figsize=GraphConfig.RESPONSE_TIME_FIGSIZE)
        
        sns.histplot(
            data=df,
            x='response_time',
            hue='priority',
            element='step',
            stat='density',
            common_norm=False,
            binwidth=1
        )
        
        # Add threshold lines
        plt.axvline(x=30, color='r', linestyle='--', label='30 min threshold')
        plt.axvline(x=60, color='g', linestyle='--', label='60 min threshold')
        
        # Configure plot
        plt.title(f'Response Time Distribution by Priority - {division}\n{start_date} to {end_date}')
        plt.xlabel('Response Time (minutes)')
        plt.ylabel('Density')
        plt.legend(title='Priority')
        plt.xlim(0, df['response_time'].quantile(0.99))
        plt.tight_layout()
        
        # Save plot
        filename = f'response_time_distribution_{division}_{start_date.replace("/", "-")}_{end_date.replace("/", "-")}.png'
        return self._save_plot(filename)

class ReportGraphManager:
    """Manages the generation of all graphs for the report"""
    
    def __init__(self):
        self.output_dir = Config.OUTPUT_DIR
        self.heatmap_generator = HeatmapGenerator()
        self.response_time_generator = ResponseTimeDistributionGenerator()
    
    def generate_division_graphs(
        self,
        df: pd.DataFrame,
        division: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, str]:
        """Generate all graphs for a division"""
        # Generate heatmaps
        turned_path, cancelled_path, ran_path = self.heatmap_generator.generate_heatmaps(
            df, division, start_date, end_date
        )
        
        # Generate response time distribution
        response_time_path = self.response_time_generator.generate_distribution(
            df, division, start_date, end_date
        )
        
        return {
            'turned_heatmap': Path(turned_path).name,
            'cancelled_heatmap': Path(cancelled_path).name,
            'ran_heatmap': Path(ran_path).name,
            'response_time_distribution': Path(response_time_path).name if response_time_path else None
        }