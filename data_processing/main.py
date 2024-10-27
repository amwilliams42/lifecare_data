import json
from transport_processing import TransportDataProcessor

def main():
    processor = TransportDataProcessor()
    
    # Example date range
    start_date = "10/20/2024"
    end_date = "10/26/2024"
    
    try:
        processor.load_data(start_date, end_date)
        summary = processor.get_basic_summary()
        
        # Output summary to JSON file
        with open('report_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
            
    except Exception as e:
        print(f"Error generating report: {str(e)}")

if __name__ == "__main__":
    main()