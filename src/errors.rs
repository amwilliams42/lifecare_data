use std::error::Error;
use std::fmt;
use axum::response::{IntoResponse, Response};
use axum::http::StatusCode;

#[derive(Debug)]
pub enum AppError {
    DatabaseError(Box<dyn Error>),
    CsvError(Box<dyn Error>),
    IoError(Box<dyn Error>),
    PythonError(Box<dyn Error>),
    TemplateError(Box<dyn Error>),
    PdfGenerationError(Box<dyn Error>),
    InternalServerError(Box<dyn Error>),
    InputError(Box<dyn Error>),
    JsonError(Box<dyn Error>),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::DatabaseError(e) => write!(f, "Database error: {}", e),
            AppError::CsvError(e) => write!(f, "CSV error: {}", e),
            AppError::IoError(e) => write!(f, "I/O error: {}", e),
            AppError::PythonError(e) => write!(f, "Python error: {}", e),
            AppError::TemplateError(e) => write!(f, "Template error: {}", e),
            AppError::PdfGenerationError(e) => write!(f, "PDF generation error: {}", e),
            AppError::InternalServerError(e) => write!(f, "Internal server error: {}", e),
            AppError::InputError(e) => write!(f, "Input error: {}", e),
            AppError::JsonError(e) => write!(f, "JSON error: {}", e),
        }
    }
}

impl Error for AppError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            AppError::DatabaseError(e) => Some(e.as_ref()),
            AppError::CsvError(e) => Some(e.as_ref()),
            AppError::IoError(e) => Some(e.as_ref()),
            AppError::PythonError(e) => Some(e.as_ref()),
            AppError::TemplateError(e) => Some(e.as_ref()),
            AppError::PdfGenerationError(e) => Some(e.as_ref()),
            AppError::InternalServerError(e) => Some(e.as_ref()),
            AppError::InputError(e) => Some(e.as_ref()),
            AppError::JsonError(e) => Some(e.as_ref()),
        }
    }
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, error_message) = match self {
            AppError::DatabaseError(e) => (StatusCode::INTERNAL_SERVER_ERROR, format!("Database error: {}", e)),
            AppError::CsvError(e) => (StatusCode::BAD_REQUEST, format!("CSV error: {}", e)),
            AppError::IoError(e) => (StatusCode::INTERNAL_SERVER_ERROR, format!("I/O error: {}", e)),
            AppError::PythonError(e) => (StatusCode::INTERNAL_SERVER_ERROR, format!("Python error: {}", e)),
            AppError::TemplateError(e) => (StatusCode::INTERNAL_SERVER_ERROR, format!("Template error: {}", e)),
            AppError::PdfGenerationError(e) => (StatusCode::INTERNAL_SERVER_ERROR, format!("PDF generation error: {}", e)),
            AppError::InternalServerError(e) => (StatusCode::INTERNAL_SERVER_ERROR, format!("Internal server error: {}", e)),
            AppError::InputError(e) => (StatusCode::BAD_REQUEST, format!("Input error: {}", e)),
            AppError::JsonError(e) => (StatusCode::INTERNAL_SERVER_ERROR, format!("JSON error: {}", e)),
        };

        (status, error_message).into_response()
    }
}

// Implement From for common error types
impl From<std::io::Error> for AppError {
    fn from(err: std::io::Error) -> Self {
        AppError::IoError(Box::new(err))
    }
}

impl From<serde_json::Error> for AppError {
    fn from(err: serde_json::Error) -> Self {
        AppError::JsonError(Box::new(err))
    }
}

impl From<chrono::ParseError> for AppError {
    fn from(err: chrono::ParseError) -> Self {
        AppError::InputError(Box::new(err))
    }
}

// Add more From implementations as needed for other error types you're using