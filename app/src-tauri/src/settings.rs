use crate::models::{ChromeProfile, CustomApp, ExecutionPlan, Settings};
use std::env;
use std::fs;
use std::path::PathBuf;

fn settings_path() -> PathBuf {
    // Prefer the Tauri bundle layout: <exe_dir>/resources/settings.json (release build)
    let exe_dir = env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|p| p.to_path_buf()));

    if let Some(dir) = exe_dir.clone() {
        let candidate = dir.join("resources").join("settings.json");
        if candidate.exists() {
            return candidate;
        }
    }

    if let Ok(cwd) = env::current_dir() {
        let candidate = cwd.join("resources").join("settings.json");
        if candidate.exists() {
            return candidate;
        }
    }

    if let Some(dir) = exe_dir {
        return dir.join("settings.json");
    }

    PathBuf::from("settings.json")
}

#[tauri::command]
pub fn load_settings() -> Result<Settings, String> {
    let settings_path = settings_path();
    if settings_path.exists() {
        let content = fs::read_to_string(&settings_path)
            .map_err(|e| format!("Failed to read settings file: {}", e))?;
        let settings = serde_json::from_str(&content)
            .map_err(|e| format!("Failed to parse settings JSON: {}", e))?;
        Ok(settings)
    } else {
        Ok(Settings::default())
    }
}

#[tauri::command]
pub fn save_settings(settings: Settings) -> Result<serde_json::Value, String> {
    let settings_path = settings_path();
    let content = serde_json::to_string_pretty(&settings)
        .map_err(|e| format!("Failed to serialize settings: {}", e))?;
    fs::write(&settings_path, content)
        .map_err(|e| format!("Failed to write settings file: {}", e))?;
    use serde_json::json;
    let result = json!({
        "settings": settings,
        "path": settings_path.to_string_lossy()
    });
    Ok(result)
}

#[tauri::command]
pub fn add_execution_plan(plan: ExecutionPlan) -> Result<(), String> {
    let mut settings = load_settings()?;
    settings.execution_plans.push(plan);
    save_settings(settings).map(|_| ())
}

#[tauri::command]
pub fn update_execution_plan(index: usize, plan: ExecutionPlan) -> Result<(), String> {
    let mut settings = load_settings()?;
    if index < settings.execution_plans.len() {
        settings.execution_plans[index] = plan;
        save_settings(settings).map(|_| ())
    } else {
        Err("Execution plan index out of bounds".to_string())
    }
}

#[tauri::command]
pub fn remove_execution_plan(index: usize) -> Result<(), String> {
    let mut settings = load_settings()?;
    if index < settings.execution_plans.len() {
        settings.execution_plans.remove(index);
        save_settings(settings).map(|_| ())
    } else {
        Err("Execution plan index out of bounds".to_string())
    }
}

#[tauri::command]
pub fn add_custom_app(app: CustomApp) -> Result<(), String> {
    let mut settings = load_settings()?;
    settings.custom_apps.push(app);
    save_settings(settings).map(|_| ())
}

#[tauri::command]
pub fn update_custom_app(index: usize, app: CustomApp) -> Result<(), String> {
    let mut settings = load_settings()?;
    if index < settings.custom_apps.len() {
        settings.custom_apps[index] = app;
        save_settings(settings).map(|_| ())
    } else {
        Err("Custom app index out of bounds".to_string())
    }
}

#[tauri::command]
pub fn add_chrome_profile(profile: ChromeProfile) -> Result<(), String> {
    let mut settings = load_settings()?;
    settings.chrome_profiles.push(profile);
    save_settings(settings).map(|_| ())
}

#[tauri::command]
pub fn update_chrome_profile(index: usize, profile: ChromeProfile) -> Result<(), String> {
    let mut settings = load_settings()?;
    if index < settings.chrome_profiles.len() {
        settings.chrome_profiles[index] = profile;
        save_settings(settings).map(|_| ())
    } else {
        Err("Chrome profile index out of bounds".to_string())
    }
}

#[tauri::command]
pub fn remove_chrome_profile(index: usize) -> Result<(), String> {
    let mut settings = load_settings()?;
    if index < settings.chrome_profiles.len() {
        settings.chrome_profiles.remove(index);
        save_settings(settings).map(|_| ())
    } else {
        Err("Chrome profile index out of bounds".to_string())
    }
}
