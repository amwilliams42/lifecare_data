import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from datetime import datetime



def generate_heatmaps(df, division, start_date, end_date, output_dir):
    """Generate separate heatmaps for turns and cancels by hour and day of week."""
    # Convert start_date and end_date to datetime objects
    start_date = datetime.strptime(start_date, '%m/%d/%Y')
    end_date = datetime.strptime(end_date, '%m/%d/%Y')
    
    # Convert 'date_of_service' to datetime and filter the dataframe
    df['date_of_service'] = pd.to_datetime(df['date_of_service'])
    df = df[(df['date_of_service'] >= start_date) & (df['date_of_service'] <= end_date)]
    print(df.head())
    # Extract day of week and hour
    df['day_of_week'] = df['date_of_service'].dt.day_name()
    
    # Create a dictionary to map full day names to shortened versions
    day_map = {'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed', 
               'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'}
    
    # Apply the mapping to the 'day_of_week' column
    df['day_of_week'] = df['day_of_week'].map(day_map)
    
    # Reorder days of week
    day_order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    
    # Function to create heatmap
    def create_heatmap(data, title, filename):
        print(f"Sample of {title} data:")
        print(data[['date_of_service', 'day_of_week', 'hour']].head())
        print(f"Hour distribution:\n{data['hour'].value_counts().sort_index()}")
        plt.figure(figsize=(16, 8))  # Increased width to accommodate all hours
        pivot = pd.pivot_table(data, values='id', index='day_of_week', columns='hour', aggfunc='count', fill_value=0)
        pivot = pivot.reindex(index=day_order, columns=range(24), fill_value=0)  # Ensure all hours are present
        
        # Replace NaN values with 0 and convert to integers
        pivot = pivot.fillna(0).astype(int)
        
        sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt="d", cbar_kws={'label': 'Number of Calls'})
        plt.title(f'{title} - {division}\n{start_date.strftime("%m/%d/%Y")} to {end_date.strftime("%m/%d/%Y")}')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.xticks(range(0, 24, 1), range(24))  # Set x-axis ticks for all 24 hours
        plt.tight_layout()
        full_path = os.path.join(output_dir, filename)
        plt.savefig(full_path, dpi=300, bbox_inches='tight')
        plt.close()
        return full_path
    
    # Generate heatmap for turned calls
    turned_data = df[df['category'] == 'Turned']
    turned_path = create_heatmap(turned_data, 'Turned Calls by Hour and Day', f'turned_heatmap_{division}_{start_date.strftime("%m-%d-%Y")}_{end_date.strftime("%m-%d-%Y")}.png')
    
    # Generate heatmap for cancelled calls
    cancelled_data = df[df['category'] == 'Cancelled']
    cancelled_path = create_heatmap(cancelled_data, 'Cancelled Calls by Hour and Day', f'cancelled_heatmap_{division}_{start_date.strftime("%m-%d-%Y")}_{end_date.strftime("%m-%d-%Y")}.png')
    
    # Generate heatmap for ran calls
    ran_data = df[df['category'] == 'Ran']
    ran_path = create_heatmap(ran_data, 'Ran Calls by Hour and Day', f'ran_heatmap_{division}_{start_date.strftime("%m-%d-%Y")}_{end_date.strftime("%m-%d-%Y")}.png')
    
    return turned_path, cancelled_path, ran_path


def generate_response_time_distribution(df, division, start_date, end_date, output_dir):
    """Generate a response time distribution graph by priority."""
    print(f"Generating response time distribution for {division}")
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {df.columns}")
    print(f"Unique values in 'priority': {df['priority'].unique()}")
    print(f"Response time statistics:\n{df['response_time'].describe()}")
    
    # Ensure response_time is numeric and remove any invalid values
    df['response_time'] = pd.to_numeric(df['response_time'], errors='coerce')
    df = df.dropna(subset=['response_time', 'priority'])
    
    # Remove extreme outliers (e.g., response times > 24 hours)
    df = df[df['response_time'] <= 1440]  # 24 hours = 1440 minutes
    df = df[df['response_time'] > 0]
    
    print(f"DataFrame shape after cleaning: {df.shape}")
    print(f"Response time statistics after cleaning:\n{df['response_time'].describe()}")
    
    if df.empty:
        print("No valid data for response time distribution graph")
        return None
    
    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x='response_time', hue='priority', element='step', stat='density', common_norm=False, binwidth=1)
    plt.axvline(x=30, color='r', linestyle='--', label='30 min threshold')
    plt.axvline(x=60, color='g', linestyle='--', label='60 min threshold')
    plt.title(f'Response Time Distribution by Priority - {division}\n{start_date} to {end_date}')
    plt.xlabel('Response Time (minutes)')
    plt.ylabel('Density')
    plt.legend(title='Priority')
    plt.xlim(0, df['response_time'].quantile(0.99))  # Set x-axis limit to 99th percentile
    plt.tight_layout()
    
    # Save the figure
    filename = f'response_time_distribution_{division}_{start_date.replace("/", "-")}_{end_date.replace("/", "-")}.png'
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Response time distribution graph saved to {filepath}")
    return os.path.abspath(filepath)