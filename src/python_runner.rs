use std::process::Command;
use std::path::Path;
use chrono::NaiveDate;
use crate::errors::AppError;

pub fn run_python_script(start_date: &NaiveDate, end_date: &NaiveDate) -> Result<String, AppError> {
    #[cfg(target_os = "linux")]
    fn run() {
        let venv_activate = Path::new("./data_processing/venv/bin/activate");

    }

    let script_path = Path::new("./data_processing/main.py");

    let start_date_str = start_date.format("%m/%d/%Y").to_string();
    let end_date_str = end_date.format("%m/%d/%Y").to_string();

    println!("Executing Python script with dates: {} to {}", start_date_str, end_date_str);

    #[cfg(target_os = "linux")]
    let command = format!(
        "source {} && python {} {} {}",
        venv_activate.display(),
        script_path.display(),
        start_date_str,
        end_date_str
    );

    #[cfg(target_os = "windows")]
    let command = format!(
        "python3 {} {} {}",
        script_path.display(),
        start_date_str,
        end_date_str
    );

    println!("Executing command: {}", command);

    let output = Command::new("bash")
        .arg("-c")
        .arg(&command)
        .output()
        .map_err(|e| AppError::PythonError(format!("Failed to execute Python script: {}", e).into()))?;

    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        let stdout = String::from_utf8_lossy(&output.stdout);
        println!("Python script stderr: {}", stderr);
        println!("Python script stdout: {}", stdout);
        return Err(AppError::PythonError(format!(
            "Python script failed. Stderr: {}, Stdout: {}",
            stderr, stdout
        ).into()));
    }

    let json_file_name = format!("report_{}_{}.json",
        start_date.format("%m-%d-%Y"),
        end_date.format("%m-%d-%Y")
    );

    println!("Python script executed successfully. JSON file: {}", json_file_name);

    Ok(json_file_name)
}