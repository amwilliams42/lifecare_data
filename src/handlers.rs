use axum::{
    body::Body, debug_handler, extract::{Multipart, State, Path as axPath}, http::Response, response::{Html, IntoResponse}, Form, Json
};
use chrono::NaiveDate;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::fs::File;
use tokio::io::AsyncWriteExt;
use std::path::Path;
use minijinja::context;
use crate::{csv_processor::process_csv, errors::AppError, latex_generator::{generate_latex_files, render_pdfs}, AppState, StateType};
use sqlx::Row;
use crate::python_runner::run_python_script;
use tokio_util::io::ReaderStream;



pub(crate) async fn index_handler(State(state): StateType) 
    -> Html<String> {
        let template = state.jinja.get_template("index").unwrap();
        Html(template.render(context!()).unwrap())
    }

#[debug_handler(state = Arc<AppState>)]
pub(crate) async fn upload_handler(
    State(state): StateType,
    mut multipart: Multipart)
     -> Html<String> {
        while let Some(field) = multipart.next_field().await.unwrap() {
            if let Some(file_name) = field.file_name() {
                let file_name = sanitize_filename::sanitize(file_name);
                let file_path = Path::new("uploads").join(&file_name);
                
                match field.bytes().await {
                    Ok(data) => {
                        match File::create(&file_path).await {
                            Ok(mut file) => {
                                match file.write_all(&data).await {
                                    Ok(_) => {
                                        match process_csv(&file_path, &state.db_pool).await {
                                            Ok((inserted, skipped)) => return Html(format!(
                                                "File '{}' uploaded and processed successfully. {} records inserted, {} duplicate records skipped.",
                                                file_name, inserted, skipped
                                            )),
                                            Err(e) => return Html(format!("Error processing CSV file: {}", e)),
                                        }
                                    },
                                    Err(e) => {
                                        return Html(format!("Error Writing File: {}", e));
                                    },
                                }
                            },
                            Err(e) => return Html(format!("error creating file: {}", e)),
                        }
                    },
                    Err(e) => return Html(format!("Error Reading File:{}", e)),
                }
            } else {
                return Html("No file name provided".to_string());
            }
        }
        
        Html("No file uploaded".to_string())
    }


pub(crate) async fn get_row_count(State(state): StateType) -> Json<u64> {
    let count = sqlx::query("SELECT COUNT(*) FROM records")
        .fetch_one(&state.db_pool)
        .await
        .map(|row| row.get(0))
        .unwrap_or(0);

    Json(count)
}

pub async fn download_handler(axPath(filename): axPath<String>) -> Result<Response<Body>, AppError> {
    let path = format!("completed_reports/{}", filename);
    let file = File::open(path).await.map_err(|e| AppError::IoError(Box::new(e)))?;
    let stream = ReaderStream::new(file);
    let body = Body::from_stream(stream);

    let response = Response::builder()
        .header("content-type", "application/pdf")
        .header("content-disposition", format!("attachment; filename=\"{}\"", filename))
        .body(body)
        .map_err(|e| AppError::InternalServerError(Box::new(e)))?;

    Ok(response)
}

#[derive(Deserialize, Debug)]
pub struct ReportParams {
    start_date: String,
    end_date: String,
}

#[derive(Serialize)]
pub struct ReportResponse {
    json_file: String,
}

pub async fn generate_report_handler(
    State(_state): State<Arc<AppState>>,
    Form(params): Form<ReportParams>,
) -> Result<impl IntoResponse, AppError> {
    let start_date = NaiveDate::parse_from_str(&params.start_date, "%Y-%m-%d")
        .map_err(|e| AppError::InputError(Box::new(e)))?;

    let end_date = NaiveDate::parse_from_str(&params.end_date, "%Y-%m-%d")
        .map_err(|e| AppError::InputError(Box::new(e)))?;

    let json_file = run_python_script(&start_date, &end_date)?;

    let latex_files = generate_latex_files(&json_file, "templates/report_template.tex", "output")?;

    let pdf_files = render_pdfs(&latex_files, &start_date, &end_date)?;

    let download_links = pdf_files.iter().map(|file| {
        let filename = std::path::Path::new(file)
            .file_name()
            .and_then(|s| s.to_str())
            .unwrap_or("unknown.pdf");
        format!(r#"<li><a href="/download/{}">{}</a></li>"#, filename, filename)
    }).collect::<String>();

    let html_response = format!(
        r#"
        <div id="result">
            <p>Report generated successfully!</p>
            <p>PDF files generated for {} divisions.</p>
            <ul>
            {}
            </ul>
        </div>
        "#,
        pdf_files.len(),
        download_links
    );

    Ok(Html(html_response))
}