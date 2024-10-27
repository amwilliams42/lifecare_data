use sqlx::{sqlite::SqlitePoolOptions, Pool, Sqlite, SqlitePool};

use crate::{errors::AppError, models::DatabaseRow};

pub(crate) async fn migrate(pool: &Pool<Sqlite>) -> Result<(),  Box<dyn std::error::Error>> {
    let _ = sqlx::query(
        "
        CREATE TABLE IF NOT EXISTS records (
            id integer primary key,
            date_of_service text,
            division text,
            priority text,
            category text,
            level text,
            weekday text,
            hour integer,
            origin text,
            response_time integer)").execute(pool).await?;

    Ok(())
}

pub(crate) async fn insert_row(pool: &Pool<Sqlite>, row: DatabaseRow) -> Result<(), AppError> {
    let _ = sqlx::query(
        r#"
        INSERT INTO records (
            id, date_of_service, division, priority, category, 
            level, weekday, hour, origin,
            response_time
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
        "#)
        .bind(row.id)
        .bind(row.date_of_service)
        .bind(row.division)
        .bind(row.priority)
        .bind(row.category)
        .bind(row.level)
        .bind(row.weekday)
        .bind(row.hour)
        .bind(row.origin)
        .bind(row.response_time)
    
    .execute(pool)
    .await;
    
    Ok(())
}