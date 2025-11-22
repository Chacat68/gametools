// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::Command;
use tauri::Manager;

// Tauri命令：调用Python脚本执行越南文检测
#[tauri::command]
fn run_vietnamese_scanner(directory: String, output: String, recursive: bool) -> Result<String, String> {
    let python_exe = if cfg!(windows) { "python" } else { "python3" };
    
    let mut cmd = Command::new(python_exe);
    cmd.arg("../core/vietnamese_excel_processor.py")
        .arg(&directory)
        .arg(&output)
        .arg(if recursive { "--recursive" } else { "--no-recursive" });
    
    match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                Ok(String::from_utf8_lossy(&output.stdout).to_string())
            } else {
                Err(String::from_utf8_lossy(&output.stderr).to_string())
            }
        }
        Err(e) => Err(format!("执行失败: {}", e)),
    }
}

// Tauri命令：调用JSON格式检测
#[tauri::command]
fn run_json_detector(path: String) -> Result<String, String> {
    let python_exe = if cfg!(windows) { "python" } else { "python3" };
    
    let mut cmd = Command::new(python_exe);
    cmd.arg("../tools/json_error_detector/json_error_detector.py")
        .arg(&path);
    
    match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                Ok(String::from_utf8_lossy(&output.stdout).to_string())
            } else {
                Err(String::from_utf8_lossy(&output.stderr).to_string())
            }
        }
        Err(e) => Err(format!("执行失败: {}", e)),
    }
}

// Tauri命令：调用Excel数据处理
#[tauri::command]
fn run_excel_processor(input_file: String, output_folder: String, mode: String) -> Result<String, String> {
    let python_exe = if cfg!(windows) { "python" } else { "python3" };
    
    let mut cmd = Command::new(python_exe);
    cmd.arg("../tools/excel_data_processor.py")
        .arg(&input_file)
        .arg(&output_folder)
        .arg("--mode")
        .arg(&mode);
    
    match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                Ok(String::from_utf8_lossy(&output.stdout).to_string())
            } else {
                Err(String::from_utf8_lossy(&output.stderr).to_string())
            }
        }
        Err(e) => Err(format!("执行失败: {}", e)),
    }
}

// Tauri命令：调用字段提取工具
#[tauri::command]
fn run_field_extractor(directory: String, output_folder: String, format: String, recursive: bool) -> Result<String, String> {
    let python_exe = if cfg!(windows) { "python" } else { "python3" };
    
    let mut cmd = Command::new(python_exe);
    cmd.arg("../core/excel_field_extractor.py")
        .arg(&directory)
        .arg(&output_folder)
        .arg("--format")
        .arg(&format)
        .arg(if recursive { "--recursive" } else { "--no-recursive" });
    
    match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                Ok(String::from_utf8_lossy(&output.stdout).to_string())
            } else {
                Err(String::from_utf8_lossy(&output.stderr).to_string())
            }
        }
        Err(e) => Err(format!("执行失败: {}", e)),
    }
}

// Tauri命令：调用多语言翻译提取
#[tauri::command]
fn run_translation_extractor(json_config: String, lang_dirs: Vec<String>, output_file: String) -> Result<String, String> {
    let python_exe = if cfg!(windows) { "python" } else { "python3" };
    
    let mut cmd = Command::new(python_exe);
    cmd.arg("../core/table_range_translator.py")
        .arg(&json_config)
        .arg(&output_file);
    
    // 添加多个语言目录
    for dir in lang_dirs {
        cmd.arg("--lang-dir").arg(&dir);
    }
    
    match cmd.output() {
        Ok(output) => {
            if output.status.success() {
                Ok(String::from_utf8_lossy(&output.stdout).to_string())
            } else {
                Err(String::from_utf8_lossy(&output.stderr).to_string())
            }
        }
        Err(e) => Err(format!("执行失败: {}", e)),
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            run_vietnamese_scanner,
            run_json_detector,
            run_excel_processor,
            run_field_extractor,
            run_translation_extractor
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
