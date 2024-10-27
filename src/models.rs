use serde::{Deserialize, Serialize};
use chrono::{Datelike, NaiveDateTime, Timelike};

use crate::types::*;



#[derive(Debug, Clone, Deserialize)]
pub struct CSVRecord {
    #[serde(rename(deserialize = "Pickup Time"))]
    #[serde(with="parse_time")]
    pub pickup_time: NaiveDateTime,
    #[serde(rename(deserialize = "Company Name"))]
    pub company_name: String,
    #[serde(rename(deserialize = "Division"))]
    pub division: Division,
    #[serde(rename(deserialize = "Vehicle"))]
    pub vehicle: String,
    #[serde(rename(deserialize = "Trip Type Name"))]
    pub trip_type_name: String,
    #[serde(rename(deserialize = "Priority Name"))]
    pub priority_name: String,
    #[serde(rename(deserialize = "Origin Name"))]
    pub origin_name: String,
    #[serde(rename(deserialize = "CallTakerStatus"))]
    pub call_taker_status: String,
    #[serde(rename(deserialize = "Confirmation #"))]
    pub confirmation_number: i32,
    #[serde(rename(deserialize = "Date of Service"))]
    #[serde(with="parse_time")]
    pub date_of_service: NaiveDateTime,
    #[serde(rename(deserialize = "Enroute"))]
    #[serde(with="parse_time")]
    pub enroute_time: NaiveDateTime,
    #[serde(rename(deserialize = "At Scene"))]
    #[serde(with="parse_time")]
    pub at_scene_time: NaiveDateTime,
    #[serde(rename(deserialize = "At Destination"))]
    #[serde(with="parse_time")]
    pub at_destination_time: NaiveDateTime,
    #[serde(rename(deserialize = "Assigned"))]
    #[serde(with="parse_time")]
    pub assigned_time: NaiveDateTime,
    #[serde(rename(deserialize = "Complete"))]
    #[serde(with="parse_time")]
    pub complete_time: NaiveDateTime,
}

pub mod parse_time {
    use serde::{Deserialize, Serializer, Deserializer, Serialize};
	use chrono::naive::NaiveDateTime;

    pub fn serialize<S>(
        dt: &NaiveDateTime,
        serializer: S,
    ) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        dt.format("%m/%d/%Y %I:%M:%S").to_string().serialize(serializer)
    }

    pub fn deserialize<'de, D>(deserializer: D) -> Result<NaiveDateTime, D::Error>
where
    D: Deserializer<'de>,
{
    let s: String = String::deserialize(deserializer)?;
    let trimmed = s.trim();
    
    if trimmed.is_empty() {
        // Return a default value for empty input
        return Ok(NaiveDateTime::from_timestamp(0, 0)); // Unix Epoch
    }

    // Try parsing with different formats
    for format in &["%m/%d/%Y %H:%M:%S %p", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%D %I:%M:%S %p", "%D %r", "%m/%d/%Y %I:%M:%S %p"] {
        if let Ok(dt) = NaiveDateTime::parse_from_str(trimmed, format) {
            return Ok(dt);
        }
    }

    // If all parsing attempts fail, return an error
    Err(serde::de::Error::custom(format!("Invalid datetime: {}", trimmed)))
}

fn get_default_datetime() -> Result<NaiveDateTime, chrono::ParseError> {
    // You can adjust this default value as needed
    NaiveDateTime::parse_from_str("01/01/2030 00:00:00", "%m/%d/%Y %I:%M:%S")
}

}




#[derive(Debug, Deserialize, Serialize)]
pub struct DatabaseRow {
    pub id: i32,
    pub date_of_service: String,
    pub division: Division,
    pub priority: Priority,
    pub category: CallCategory,
    pub level: CallLevel,
    pub weekday: Day,
    pub hour: u32,
    pub origin: String,
    pub response_time: i64,
}



impl From<CSVRecord> for DatabaseRow{
    fn from(value: CSVRecord) -> Self {
        DatabaseRow{
            id: value.confirmation_number,
            division: Division::from(value.division),
            priority: Priority::from(value.priority_name.clone()),
            category: CallCategory::from(value.call_taker_status.clone()),
            level: CallLevel::from(value.trip_type_name.clone()),
            weekday: value.date_of_service.weekday().into(),
            hour: value.pickup_time.hour(),
            origin: value.origin_name.clone(),
            response_time: {
                match CallCategory::from(value.call_taker_status.clone()) {
                    CallCategory::Ran => {
                        (value.at_scene_time - value.assigned_time).num_minutes()
                    },
                    CallCategory::Turned => 0,
                    CallCategory::Cancelled => 0,
                }
                },
            date_of_service: {
                value.date_of_service.format("%D").to_string()
            },            
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    
    
    #[test]
    fn test_to_database_row() -> Result<(), Box<dyn std::error::Error>> {
        let mut reader = csv::ReaderBuilder::new()
            .quoting(true)
            .from_path("./uploads/test.csv")?;

        for record in reader.deserialize() {
            let record: CSVRecord = record?;
            let dbrow = DatabaseRow::from(record.clone());
            println!("{:?}", record);
            println!("{:?}", dbrow);
        }
        Ok(())
        
    }
}

