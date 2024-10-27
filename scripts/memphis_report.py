import pandas as pd
from origin_report import latex_escape, format_delta

methodist_names = [
    "METHODIST HOSPITAL - UNIVERSITY",
    "METHODIST HOSPITAL - GERMANTOWN",
    "METHODIST HOSPITAL - NORTH",
    "METHODIST HOSPITAL - SOUTH",
    "METHODIST HOSPITAL - OLIVE BRANCH"
]

baptist_names = [
    "BAPTIST MEMORIAL HOSPITAL - DESOTO",
    "BAPTIST MEMORIAL HOSPITAL - MEMPHIS",
    "BAPTIST MEMORIAL HOSPITAL - TIPTON",
    "BAPTIST MEMORIAL HOSPITAL - CHILDREN",
    "BAPTIST MEMORIAL HOSPITAL -  ARLINGTON ER"
]

st_francis_names = [
    "ST FRANCIS HOSPITAL - BARTLETT",
    "ST FRANCIS HOSPITAL - PARK"
]

def generate_specialized_origin_table(df, hospital_names, start_date, end_date, compare_days):
    """Generate a specialized origin table for specific hospitals."""
    start_date = pd.to_datetime(start_date, format='%m/%d/%Y')
    end_date = pd.to_datetime(end_date, format='%m/%d/%Y')
    
    prev_start_date = start_date - pd.Timedelta(days=compare_days)
    prev_end_date = start_date - pd.Timedelta(days=1)
    
    # Filter data for current period and previous period
    current_period_data = df[(df['date_of_service'] >= start_date) & (df['date_of_service'] <= end_date)]
    prev_period_data = df[(df['date_of_service'] >= prev_start_date) & (df['date_of_service'] <= prev_end_date)]
    
    def process_data(data, hospital_names):
        data = data[data['category'] == 'Ran']
        data = data[data['origin'].isin(hospital_names)]
        summary_df = data.groupby('origin')['level'].value_counts().unstack(fill_value=0)

        expected_columns = ['ALS', 'BLS', 'CCU']
        for col in expected_columns:
            if col not in summary_df.columns:
                summary_df[col] = 0
        
        summary_df = summary_df[expected_columns]
        summary_df['Total'] = summary_df.sum(axis=1)
        summary_df = summary_df.reset_index()
        summary_df = summary_df[['origin', 'ALS', 'BLS', 'CCU', 'Total']]

        for col in ['ALS', 'BLS', 'CCU', 'Total']:
            summary_df[col] = summary_df[col].astype(int)
        
        return summary_df
    
    current_summary = process_data(current_period_data, hospital_names)
    prev_summary = process_data(prev_period_data, hospital_names)
    
    merged_summary = current_summary.merge(prev_summary[['origin', 'Total']], on='origin', how='outer', suffixes=('', '_prev'))
    merged_summary = merged_summary.fillna(0)
    
    merged_summary['PrevTotal'] = merged_summary['Total_prev'].astype(int)
    merged_summary['Delta'] = (merged_summary['Total'] - merged_summary['PrevTotal']).astype(int)
    merged_summary['Delta'] = merged_summary['Delta'].apply(format_delta)
    
    merged_summary = merged_summary.drop(columns=['Total_prev'])
    merged_summary = merged_summary.sort_values('origin')
    
    totals = merged_summary.sum(numeric_only=True).astype(int)
    totals['origin'] = 'TOTAL'
    totals['Delta'] = format_delta(totals['Total'] - totals['PrevTotal'])

    numeric_columns = ['ALS', 'BLS', 'CCU', 'Total', 'PrevTotal']
    for column in numeric_columns:
        if column in merged_summary.columns:
            merged_summary[column] = merged_summary[column].astype(int)
 
    hline_row = pd.DataFrame([{col: '\\hline' if col == 'origin' else '' for col in merged_summary.columns}])
    
    merged_summary = pd.concat([merged_summary, hline_row, pd.DataFrame([totals])], ignore_index=True)
    
    merged_summary['origin'] = merged_summary['origin'].apply(lambda x: latex_escape(x) if x != '\\hline' else x)
    
    return merged_summary.to_dict(orient='records')

def generate_memphis_report(df, start_date, end_date, compare_days):
    """Generate specialized reports for Memphis division."""
    methodist_table = generate_specialized_origin_table(df, methodist_names, start_date, end_date, compare_days)
    baptist_table = generate_specialized_origin_table(df, baptist_names, start_date, end_date, compare_days)
    st_francis_table = generate_specialized_origin_table(df, st_francis_names, start_date, end_date, compare_days)
    
    return {
        "methodist_table": methodist_table,
        "baptist_table": baptist_table,
        "st_francis_table": st_francis_table
    }   