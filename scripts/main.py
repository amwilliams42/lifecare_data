import json
from datetime import datetime
import os
from database import connect_to_database, fetch_data
from origin_report import generate_origin_report
from graphs import generate_heatmaps, generate_response_time_distribution
from memphis_report import generate_memphis_report
from summary_table import generate_summary_table

def parse_date(date_string):
    """Parse date string in MM/DD/YYYY format."""
    return datetime.strptime(date_string, "%m/%d/%Y")

def ensure_output_directory():
    """Ensure the tmp_output directory exists."""
    output_dir = "tmp_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def generate_division_report(df, division, start_date, end_date, output_dir):
    """Generate a complete report for a single division."""
    df_division = df[df['division'] == division]
    
    date_range = (parse_date(end_date) - parse_date(start_date)).days + 1
    
    origin_report = generate_origin_report(df_division, start_date, end_date, date_range)
    summary_table = generate_summary_table(df_division, start_date, end_date)
    
    turned_path, cancelled_path, ran_path = generate_heatmaps(df_division, division, start_date, end_date, output_dir)

    response_time_path = generate_response_time_distribution(df_division, division, start_date, end_date, output_dir)

    
    report = {
        "division": division,
        "start_date": start_date,
        "end_date": end_date,
        "total_records": len(df_division),
        "summary_table": summary_table,
        "origin_report": origin_report,
        "turned_heatmap": os.path.basename(turned_path),
        "cancelled_heatmap": os.path.basename(cancelled_path),
        "ran_heatmap": os.path.basename(ran_path),
        "response_time_distribution": os.path.basename(response_time_path)
    }

    if division == "Memphis":
        memphis_report = generate_memphis_report(df_division, start_date, end_date, date_range)
        report["memphis_specialized_report"] = memphis_report
    
    return report

def main(start_date, end_date):
    """Main function to generate separate reports for each division."""
    print(f"Querying data for date range: {start_date} to {end_date}")
    
    conn = connect_to_database()
    df = fetch_data(conn, start_date, end_date)
    output_dir = ensure_output_directory()
    
    if df.empty:
        print("No data fetched. Please check the date range and database contents.")
        return json.dumps({"error": "No data found for the specified date range"})
    
    print(f"Total records fetched: {len(df)}")
    print(f"Unique divisions: {df['division'].unique()}")
    print(f"Records per division:")
    print(df['division'].value_counts())
    
    # Get unique divisions
    divisions = df['division'].unique()
    
    reports = {}
    for division in divisions:
        reports[division] = generate_division_report(df, division, start_date, end_date, output_dir)
    
    conn.close()
    print(df.head())
    return reports  # Return the reports dictionary, not the JSON string

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python main.py start_date end_date")
        print("Date format: MM/DD/YYYY")
        sys.exit(1)
    
    start_date, end_date = sys.argv[1], sys.argv[2]
    result = main(start_date, end_date)
    
    # Convert the result to JSON and print it once
    json_result = json.dumps(result, indent=2)

    output_dir = ensure_output_directory()
    filename = os.path.join(output_dir, f"report_{start_date.replace('/', '-')}_{end_date.replace('/', '-')}.json")

    
    # Write the JSON to a file
    with open(filename, 'w') as f:
        f.write(json_result)
    
    print(f"\nReport has been written to {os.path.abspath(filename)}")