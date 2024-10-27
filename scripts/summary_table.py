import pandas as pd

def generate_summary_table(df, start_date, end_date):
    """Generate a weekly summary table."""
    # Define the days of the week

    start_date = pd.to_datetime(start_date, format='%m/%d/%Y')
    end_date = pd.to_datetime(end_date, format='%m/%d/%Y')
    df = df[(df['date_of_service'] >= start_date) & (df['date_of_service'] <= end_date)]

    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Initialize the summary DataFrame
    summary = pd.DataFrame(0, index=['ALS Ran', 'BLS Ran', 'CCU Ran', 'Total Ran', 'Turned', 'Cancelled', 'Total Missed', 'Total Demand'], 
                           columns=days + ['Total'])
    
    # Ensure 'date_of_service' is datetime
    df['date_of_service'] = pd.to_datetime(df['date_of_service'])
    
    # Add 'Day' column
    df['Day'] = df['date_of_service'].dt.day_name()
    
    # Fill the summary DataFrame
    for day in days:
        day_data = df[df['Day'] == day]
        
        summary.loc['ALS Ran', day] = day_data[(day_data['level'] == 'ALS') & (day_data['category'] == 'Ran')].shape[0]
        summary.loc['BLS Ran', day] = day_data[(day_data['level'] == 'BLS') & (day_data['category'] == 'Ran')].shape[0]
        summary.loc['CCU Ran', day] = day_data[(day_data['level'] == 'CCU') & (day_data['category'] == 'Ran')].shape[0]
        summary.loc['Total Ran', day] = summary.loc[['ALS Ran', 'BLS Ran', 'CCU Ran'], day].sum()
        
        summary.loc['Turned', day] = day_data[day_data['category'] == 'Turned'].shape[0]
        summary.loc['Cancelled', day] = day_data[day_data['category'] == 'Cancelled'].shape[0]
        summary.loc['Total Missed', day] = summary.loc[['Turned', 'Cancelled'], day].sum()
        
        summary.loc['Total Demand', day] = summary.loc[['Total Ran', 'Total Missed'], day].sum()
    
    # Calculate totals
    summary['Total'] = summary[days].sum(axis=1)
    
    # Convert to integers
    summary = summary.astype(int)
    
    return summary.to_dict(orient='index')