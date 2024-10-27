import pandas as pd
from datetime import datetime, timedelta

def latex_escape(text):
    """Escape special characters for LaTeX."""
    escapes = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    return ''.join(escapes.get(c, c) for c in str(text))

def format_delta(delta):
    """Format delta value with LaTeX color and bold."""
    if delta > 0:
        return r'\textcolor{green}{\textbf{+' + str(delta) + '}}'
    elif delta < 0:
        return r'\textcolor{red}{\textbf{' + str(delta) + '}}'
    else:
        return str(delta)

def generate_top_5_table(df, category):
    """Generate a table of top 5 origins for a specific category."""
    # Convert the category column to numeric, ignoring any non-numeric strings
    df = df[df['origin'] != 'TOTAL']
    df[category] = pd.to_numeric(df[category], errors='coerce')
    
    df = df[df[category] > 0]
    # Sort the dataframe by the category column and take the top 5
    top_5 = df.sort_values(by=category, ascending=False).head(5)
    
    # Select only the origin and category columns
    top_5 = top_5[['origin', category]]
    
    return top_5.to_dict(orient='records')


def generate_origin_report(df, start_date, end_date, compare_days):
    """Generate the Origin Report."""
    start_date = pd.to_datetime(start_date, format='%m/%d/%Y')
    end_date = pd.to_datetime(end_date, format='%m/%d/%Y')
    
    prev_start_date = start_date - timedelta(days=compare_days)
    prev_end_date = start_date - timedelta(days=1)
    
    print(f"\nGenerating Origin Report for date range: {start_date.date()} to {end_date.date()}")
    print(f"Comparing with previous {compare_days} days: {prev_start_date.date()} to {prev_end_date.date()}")
    
    # Filter data for current period and previous period
    current_period_data = df[(df['date_of_service'] >= start_date) & (df['date_of_service'] <= end_date)]
    prev_period_data = df[(df['date_of_service'] >= prev_start_date) & (df['date_of_service'] <= prev_end_date)]
    
    def process_data(data):
        data = data[data['category'] == 'Ran']
        summary_df = data.groupby('origin')['level'].value_counts().unstack(fill_value=0)

        # Rename the columns to match your desired output
        expected_columns = ['ALS', 'BLS', 'CCU']
        for col in expected_columns:
            if col not in summary_df.columns:
                summary_df[col] = 0
        
        # Reorder columns to match desired output
        summary_df = summary_df[expected_columns]


        # Calculate the total calls for each origin
        summary_df['Total'] = summary_df.sum(axis=1)

        for col in ['ALS', 'BLS', 'CCU', 'Total']:
            summary_df[col] = summary_df[col].astype(int)

        # Reset the index to make 'Origin' a column
        summary_df = summary_df.reset_index()

        # Reorder the columns to match your desired output
        summary_df = summary_df[['origin', 'ALS', 'BLS', 'CCU', 'Total']]
        
        return summary_df
    
    current_summary = process_data(current_period_data)
    prev_summary = process_data(prev_period_data)
    
    # Merge current and previous summaries, keeping all origins from both periods
    merged_summary = current_summary.merge(prev_summary[['origin', 'Total']], on='origin', how='outer', suffixes=('', '_prev'))
    
    # Fill NaN values with 0 for origins not present in current week
    merged_summary = merged_summary.fillna(0)
    
    merged_summary['PrevTotal'] = merged_summary['Total_prev'].astype(int)
    merged_summary['Delta'] = (merged_summary['Total'] - merged_summary['PrevTotal']).astype(int)
    
    # Format Delta column
    merged_summary['Delta'] = merged_summary['Delta'].apply(format_delta)
    
    # Drop the temporary 'Total_prev' column
    merged_summary = merged_summary.drop(columns=['Total_prev'])
    
    # Sort by origin
    merged_summary = merged_summary.sort_values('origin')
    
    # Calculate totals
    totals = merged_summary.sum(numeric_only=True).astype(int)
    totals['origin'] = 'TOTAL'
    totals['Delta'] = format_delta(totals['Total'] - totals['PrevTotal'])

    for col in ['ALS', 'BLS', 'CCU', 'Total']:
        merged_summary[col] = merged_summary[col].astype(int)
    
 

    numeric_columns = ['ALS', 'BLS', 'CCU', 'Total', 'PrevTotal']
    for column in numeric_columns:
        if column in merged_summary.columns:
            merged_summary[column] = merged_summary[column].astype(int)

    # Reformat Delta column
    merged_summary['Delta'] = merged_summary.apply(
        lambda row: format_delta(int(row['Total'] - row['PrevTotal']))
        if row['origin'] != '\\hline' else row['Delta'],
        axis=1
    )

    # Add a row with a special marker for hline
    hline_row = pd.DataFrame([{col: '\\hline' if col == 'origin' else 0 for col in merged_summary.columns}])
    
    # Append hline row and totals to the merged_summary DataFrame
    merged_summary = pd.concat([merged_summary, hline_row, pd.DataFrame([totals])], ignore_index=True)
    
    # Escape special characters in origin names
    merged_summary['origin'] = merged_summary['origin'].apply(lambda x: latex_escape(x) if x != '\\hline' else x)

    top_5_als = generate_top_5_table(merged_summary, 'ALS')
    top_5_bls = generate_top_5_table(merged_summary, 'BLS')
    top_5_ccu = generate_top_5_table(merged_summary, 'CCU')
    top_5_total = generate_top_5_table(merged_summary, 'Total')
    
    # Convert to dict for JSON serialization
    return {
        'full_report': merged_summary.to_dict(orient='records'),
        'top_5_als': top_5_als,
        'top_5_bls': top_5_bls,
        'top_5_ccu': top_5_ccu,
        'top_5_total': top_5_total
    }