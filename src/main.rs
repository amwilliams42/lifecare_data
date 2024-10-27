mod handlers;
mod models;
mod csv_processor;
mod database;
mod types;
mod errors;
mod latex_generator;
mod python_runner;

use axum::{
    extract::State,
    routing::{get, post}, Router,
};
use minijinja::Environment;
use sqlx::sqlite::SqlitePool;
use std::sync::Arc;



const DB_URL: &str = "sqlite:data.db";

#[derive(Clone)]
struct AppState{
    db_pool: SqlitePool,
    jinja: Environment<'static>
}

type StateType = State<Arc<AppState>>;

#[tokio::main]
async fn main() {


    let db_pool = SqlitePool::connect(DB_URL).await.unwrap();

    database::migrate(&db_pool).await.unwrap();
    
    let mut jinja = Environment::new();
    jinja.add_template("index", include_str!("../templates/index.html")).unwrap();

    let state = Arc::new(AppState{db_pool, jinja});


    let app = Router::new()
        .route("/", get(handlers::index_handler))
        .route("/upload", post(handlers::upload_handler))
        .route("/generate_report", post(handlers::generate_report_handler))
        .route("/row_count", get(handlers::get_row_count))
        .route("/download/:filename", get(handlers::download_handler))
        .with_state(state);
    
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await.unwrap();
    axum::serve(listener, app).await.unwrap();

}