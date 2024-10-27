use std::error::Error;
use std::error::Error as StdError;
use chrono::Weekday;
use serde::{Deserialize, Serialize};
use sqlx::encode::IsNull;
use sqlx::{Encode, Decode, Type, Sqlite};
use sqlx::sqlite::{SqliteArgumentValue, SqliteTypeInfo, SqliteValueRef};

#[derive(Debug, Clone, Deserialize, Serialize, Copy)]
pub enum Division {
    Memphis,
    Nashville,
    #[serde(rename(deserialize = "Special Event"))]
    SpecialEvent,
}


impl Type<Sqlite> for Division {
    fn type_info() -> SqliteTypeInfo {
        <str as Type<Sqlite>>::type_info()
    }
}

impl Encode<'_, Sqlite> for Division {
    fn encode_by_ref(&self, args: &mut Vec<SqliteArgumentValue<'_>>) -> Result<IsNull, Box<dyn StdError + Send + Sync>> {
        let s = match self {
            Division::Memphis => "Memphis",
            Division::Nashville => "Nashville",
            Division::SpecialEvent => "Special Event",
        };
        <&str as Encode<Sqlite>>::encode(s, args)
    }
}


impl Decode<'_, Sqlite> for Division {
    fn decode(value: SqliteValueRef<'_>) -> Result<Self, Box<dyn std::error::Error + 'static + Send + Sync>> {
        let value = <&str as Decode<Sqlite>>::decode(value)?;
        match value {
            "Memphis" => Ok(Division::Memphis),
            "Nashville" => Ok(Division::Nashville),
            "Special Event" => Ok(Division::SpecialEvent),
            _ => Err("Invalid division".into()),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, Copy)]
pub enum CallLevel {
    ALS,
    BLS,
    CCU,
    NA,
}

impl From<String> for CallLevel {
    fn from(value: String) -> Self {
        match value.as_ref() {
            "BLS" => return Self::BLS,
            "ALS" => return Self::ALS,
            "CCU" => return Self::CCU,
            _ => return Self::NA
        }
    }
}

impl Type<Sqlite> for CallLevel {
    fn type_info() -> SqliteTypeInfo {
        <str as Type<Sqlite>>::type_info()
    }
}

impl Encode<'_, Sqlite> for CallLevel {
    fn encode_by_ref(&self, args: &mut Vec<SqliteArgumentValue<'_>>) -> Result<IsNull, Box<dyn StdError + Send + Sync>> {
        let s = match self {
            CallLevel::ALS => "ALS",
            CallLevel::BLS => "BLS",
            CallLevel::CCU => "CCU",
            CallLevel::NA => "NA",
        };
        <&str as Encode<Sqlite>>::encode(s, args)
    }
}


impl Decode<'_, Sqlite> for CallLevel {
    fn decode(value: SqliteValueRef<'_>) -> Result<Self, Box<dyn std::error::Error + 'static + Send + Sync>> {
        let value = <&str as Decode<Sqlite>>::decode(value)?;
        match value {
            "ALS" => Ok(CallLevel::ALS),
            "BLS" => Ok(CallLevel::BLS),
            "CCU" => Ok(CallLevel::CCU),
            "NA" => Ok(CallLevel::NA),
            _ => Err("Invalid call level".into()),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, Copy)]
pub enum CallCategory {
    Ran,
    Turned,
    Cancelled
}

impl From<String> for CallCategory {
    fn from(value: String) -> Self {
        match value.as_ref() {
            "*TURNED CALL" => Self::Turned,
            "CANCELLED - NOT ASSIGNED" | 
            "CANCELLED - ON SCENE" | 
            "CANCELLED - PRIOR TO ARRIVAL" => Self::Cancelled,
            "CANCELLED - ERROR" => Self::Cancelled,
            _ => Self::Ran
        }
    }
}

impl Type<Sqlite> for CallCategory {
    fn type_info() -> SqliteTypeInfo {
        <str as Type<Sqlite>>::type_info()
    }
}

impl Encode<'_, Sqlite> for CallCategory {
    fn encode_by_ref(&self, args: &mut Vec<SqliteArgumentValue<'_>>) -> Result<IsNull, Box<dyn StdError + Send + Sync>> {
        let s = match self {
            CallCategory::Ran => "Ran",
            CallCategory::Turned => "Turned",
            CallCategory::Cancelled => "Cancelled",
        };
        <&str as Encode<Sqlite>>::encode(s, args)
    }
}


impl Decode<'_, Sqlite> for CallCategory {
    fn decode(value: SqliteValueRef<'_>) -> Result<Self, Box<dyn std::error::Error + 'static + Send + Sync>> {
        let value = <&str as Decode<Sqlite>>::decode(value)?;
        match value {
            "Ran" => Ok(CallCategory::Ran),
            "Turned" => Ok(CallCategory::Turned),
            "Cancelled" => Ok(CallCategory::Cancelled),
            _ => Err("Invalid call category".into()),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, Copy)]
pub enum Priority {
    Emergent,
    NonEmergent
}

impl From<String> for Priority {
    fn from(value: String) -> Self {
        match value.as_ref() {
            "P1 - Emergency" => Self::Emergent,
            _ => Self::NonEmergent
        }
    }
}

impl Type<Sqlite> for Priority {
    fn type_info() -> SqliteTypeInfo {
        <str as Type<Sqlite>>::type_info()
    }
}

impl Encode<'_, Sqlite> for Priority {
    fn encode_by_ref(&self, args: &mut Vec<SqliteArgumentValue<'_>>) -> Result<IsNull, Box<dyn StdError + Send + Sync>> {
        let s = match self {
            Priority::Emergent => "Emergent",
            Priority::NonEmergent => "Non Emergent",
        };
        <&str as Encode<Sqlite>>::encode(s, args)
    }
}


impl Decode<'_, Sqlite> for Priority {
    fn decode(value: SqliteValueRef<'_>) -> Result<Self, Box<dyn std::error::Error + 'static + Send + Sync>> {
        let value = <&str as Decode<Sqlite>>::decode(value)?;
        match value {
            "Emergent" => Ok(Priority::Emergent),
            "Non Emergent" => Ok(Priority::NonEmergent),
            _ => Err("Invalid call priority".into()),
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize, Copy)]
pub(crate) enum Day{
    Monday,
    Tuesday,
    Wednesday,
    Thursday,
    Friday,
    Saturday,
    Sunday
}

impl From<chrono::Weekday> for Day {
    fn from(value: chrono::Weekday) -> Self {
        match value {
            Weekday::Mon => Day::Monday,
            Weekday::Tue => Day::Tuesday,
            Weekday::Wed => Day::Wednesday,
            Weekday::Thu => Day::Thursday,
            Weekday::Fri => Day::Friday,
            Weekday::Sat => Day::Saturday,
            Weekday::Sun => Day::Sunday,
        }
    }
}

impl Type<Sqlite> for Day {
    fn type_info() -> SqliteTypeInfo {
        <str as Type<Sqlite>>::type_info()
    }
}

// Implement Encode for Weekday
impl Encode<'_, Sqlite> for Day {
    fn encode_by_ref(&self, args: &mut Vec<SqliteArgumentValue<'_>>) -> Result<IsNull, Box<dyn StdError + Send + Sync>> {
        let s = match self {
            Day::Monday => "Monday",
            Day::Tuesday => "Tuesday",
            Day::Wednesday => "Wednesday",
            Day::Thursday => "Thursday",
            Day::Friday => "Friday",
            Day::Saturday => "Saturday",
            Day::Sunday => "Sunday",
        };
        <&str as Encode<Sqlite>>::encode(s, args)
    }
}

// Implement Decode for Weekday
impl Decode<'_, Sqlite> for Day {
    fn decode(value: SqliteValueRef<'_>) -> Result<Self, Box<dyn StdError + Send + Sync>> {
        let value = <&str as Decode<Sqlite>>::decode(value)?;
        match value {
            "Monday" => Ok(Day::Monday),
            "Tuesday" => Ok(Day::Tuesday),
            "Wednesday" => Ok(Day::Wednesday),
            "Thursday" => Ok(Day::Thursday),
            "Friday" => Ok(Day::Friday),
            "Saturday" => Ok(Day::Saturday),
            "Sunday" => Ok(Day::Sunday),
            _ => Err("Invalid weekday".into()),
        }
    }
}