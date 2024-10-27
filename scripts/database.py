import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = "./data.db"

def connect_to_database():
    """Connect to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def fetch_data(conn, start_date, end_date):
    """Fetch data from the 'records' table within the specified date range."""
    # Convert input dates to datetime objects
    start_datetime = datetime.strptime(start_date, "%m/%d/%Y")
    end_datetime = datetime.strptime(end_date, "%m/%d/%Y")
    
    # Calculate the start date for fetching data (to include previous period)
    fetch_start_date = start_datetime - timedelta(days=(end_datetime - start_datetime).days + 1)
    
    # Adjust the query to handle the MM/DD/YY format in the database
    query = """
    SELECT * FROM records 
    WHERE strftime('%Y-%m-%d', substr('20'||substr(date_of_service, 7, 2)||'-'||substr(date_of_service, 1, 2)||'-'||substr(date_of_service, 4, 2), 1, 10)) 
    BETWEEN ? AND ?
    """
    
    # Convert dates to strings in YYYY-MM-DD format for the query
    fetch_start_str = fetch_start_date.strftime("%Y-%m-%d")
    end_date_str = end_datetime.strftime("%Y-%m-%d")
    
    print(f"\nQuerying with extended date range: {fetch_start_str} to {end_date_str}")
    
    df = pd.read_sql_query(query, conn, params=(fetch_start_str, end_date_str))
    
    print(f"\nFetched {len(df)} records from the database.")
    
    if not df.empty:
        print("Sample of fetched data:")
        print(df[['date_of_service', 'division', 'level']].head())
        print("\nUnique dates in fetched data:")
        print(sorted(df['date_of_service'].unique()))
    else:
        print("No data fetched. Checking all available dates in the database...")
        all_dates_query = "SELECT DISTINCT date_of_service FROM records ORDER BY date_of_service"
        all_dates = pd.read_sql_query(all_dates_query, conn)
        print("All available dates in the database:")
        print(sorted(all_dates['date_of_service'].unique()))
    
    # Convert 'date_of_service' to datetime
    df['date_of_service'] = pd.to_datetime(df['date_of_service'], format='%m/%d/%y')
    
    if not df.empty:
        print(f"\nDate range in fetched data after conversion: {df['date_of_service'].min()} to {df['date_of_service'].max()}")
        print("\nUnique dates in fetched data after conversion:")
        print(sorted(df['date_of_service'].unique()))
    
    return df