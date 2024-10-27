use chrono::NaiveDate;
use minijinja::Environment;
use serde_json::Value;
use std::{fs, path::Path};
use crate::errors::AppError;
use std::process::Command;


pub fn generate_latex_files(json_file_name: &str, template_path: &str, output_dir: &str) -> Result<Vec<String>, AppError> {
    println!("Starting LaTeX generation process");
    let json_file_path = Path::new("tmp_output").join(json_file_name);

    println!("JSON file path: {:?}", json_file_path);
    println!("Template path: {}", template_path);
    println!("Output directory: {}", output_dir);

    // Read the JSON file
    let json_content = fs::read_to_string(json_file_path)
        .map_err(|e| {
            println!("Error reading JSON file: {:?}", e);
            AppError::IoError(Box::new(e))
        })?;
    println!("JSON file read successfully");

    let data: Value = serde_json::from_str(&json_content)
        .map_err(|e| {
            println!("Error parsing JSON: {:?}", e);
            AppError::JsonError(Box::new(e))
        })?;
    println!("JSON parsed successfully");

    // Read the LaTeX template
    let template_content = fs::read_to_string(template_path)
        .map_err(|e| {
            println!("Error reading template file: {:?}", e);
            AppError::IoError(Box::new(e))
        })?;
    println!("LaTeX template read successfully");

    // Create a new MiniJinja environment and add the template
    let mut env = Environment::new();
    env.add_template("template", &template_content)
        .map_err(|e| {
            println!("Error adding template to MiniJinja environment: {:?}", e);
            AppError::TemplateError(Box::new(e))
        })?;
    println!("Template added to MiniJinja environment");

    // Get the template
    let template = env.get_template("template")
        .map_err(|e| {
            println!("Error getting template from MiniJinja environment: {:?}", e);
            AppError::TemplateError(Box::new(e))
        })?;
    println!("Template retrieved from MiniJinja environment");

    let mut generated_files = Vec::new();

    // Iterate over each division and generate a separate file
    for (division, division_data) in data.as_object().unwrap() {
        println!("Generating LaTeX for division: {}", division);
        let rendered = template.render(minijinja::context! {
            division => division,
            division_data => division_data
        }).map_err(|e| {
            println!("Error rendering template for division {}: {:?}", division, e);
            AppError::TemplateError(Box::new(e))
        })?;

        // Write the rendered LaTeX to a file named after the division
        let filename = format!("{}/{}_output.tex", output_dir, division);
        fs::write(&filename, rendered)
            .map_err(|e| {
                println!("Error writing LaTeX file for division {}: {:?}", division, e);
                AppError::IoError(Box::new(e))
            })?;
        
        generated_files.push(filename.clone());
        println!("LaTeX file generated for division {}: {}", division, filename);
    }

    println!("LaTeX generation process completed successfully");
    Ok(generated_files)
}

pub fn render_pdfs(latex_files: &[String], start_date: &NaiveDate, end_date: &NaiveDate) -> Result<Vec<String>, AppError> {
    let mut pdf_files = Vec::new();

    for latex_file in latex_files {
        let division = Path::new(latex_file)
            .file_stem()
            .and_then(|s| s.to_str())
            .and_then(|s| s.strip_suffix("_output"))
            .ok_or_else(|| AppError::InputError(Box::new(std::io::Error::new(
                std::io::ErrorKind::InvalidInput,
                format!("Invalid latex file name: {}", latex_file)
            ))))?;

        let output = Command::new("./tectonic")
            .args(&["--outdir", "completed_reports", latex_file])
            .output()
            .map_err(|e| AppError::PdfGenerationError(Box::new(e)))?;

        if !output.status.success() {
            return Err(AppError::PdfGenerationError(Box::new(std::io::Error::new(
                std::io::ErrorKind::Other,
                format!("Tectonic failed: {}", String::from_utf8_lossy(&output.stderr))
            ))));
        }

        let old_pdf_name = format!("completed_reports/{}_output.pdf", division);
        let new_pdf_name = format!("completed_reports/{}_{:?}_{:?}.pdf", 
            division, start_date, end_date);

        fs::rename(&old_pdf_name, &new_pdf_name)
            .map_err(|e| AppError::IoError(Box::new(e)))?;

        pdf_files.push(new_pdf_name);
    }

    Ok(pdf_files)
}