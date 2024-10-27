use std::path::Path;
use sqlx::SqlitePool;
use crate::database::insert_row;
use crate::errors::{AppError};
use crate::models::{CSVRecord, DatabaseRow};
use csv::Reader;
use tokio::fs::File;
use tokio::io::AsyncReadExt;

pub async fn process_csv(file_path: &Path, db_pool: &SqlitePool) -> Result<(usize, usize), AppError> {
    // Read the file
    let mut file = File::open(file_path).await?;
    let mut contents = Vec::new();
    file.read_to_end(&mut contents).await?;

    // Parse CSV
    let mut rdr = Reader::from_reader(contents.as_slice());
    let mut inserted_count = 0;
    let mut skipped_count = 0;

    for (index, result) in rdr.deserialize::<CSVRecord>().enumerate() {
        match result {
            Ok(record) => {
                let db_row: DatabaseRow = record.into();

                // Insert into database
                match insert_row(db_pool, db_row).await {
                    Ok(_) => inserted_count += 1,
                    Err(AppError::DatabaseError(e)) => {
                        if let Some(sqlx_error) = e.downcast_ref::<sqlx::Error>() {
                            if let sqlx::Error::Database(db_err) = sqlx_error {
                                if db_err.code() == Some("1555".into()) {
                                    skipped_count += 1;
                                    continue;
                                }
                            }
                        }
                        return Err(AppError::DatabaseError(Box::new(std::io::Error::new(
                            std::io::ErrorKind::Other,
                            format!("Error inserting row {}: {}", index + 1, e)
                        ))));
                    },
                    Err(e) => return Err(e),
                }
            },
            Err(err) => {
                let position = err.position().unwrap();
                let line = position.line();
                let row_result = rdr.records().nth(index);
                let row_data = match row_result {
                    Some(Ok(row)) => row.iter().collect::<Vec<&str>>().join(", "),
                    _ => "Unable to retrieve row data".to_string(),
                };
                return Err(AppError::CsvError(Box::new(std::io::Error::new(
                    std::io::ErrorKind::Other,
                    format!(
                        "CSV processing error at line {} (record {}): {}. Row data: {}",
                        line,
                        index + 1,
                        err,
                        row_data
                    )
                ))));
            }
        }
    }

    Ok((inserted_count, skipped_count))
}