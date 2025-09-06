use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::path::PathBuf;

#[derive(Debug, Serialize, Deserialize)]
pub struct AuthData {
    pub access_token: String,
    pub subscription_status: String,
    pub user_id: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct AuthCache {
    pub access_token: String,
    pub subscription_status: String,
    pub user_id: String,
    pub last_validated: String,
}

fn auth_cache_path() -> PathBuf {
    // Prefer the Tauri bundle layout: <exe_dir>/resources/.auth_cache
    if let Ok(exe) = env::current_exe() {
        if let Some(dir) = exe.parent() {
            let candidate = dir.join("resources").join(".auth_cache");
            if candidate.exists() {
                return candidate;
            }
        }
    }

    if let Ok(cwd) = env::current_dir() {
        return cwd.join("resources").join(".auth_cache");
    }

    env::current_exe()
        .ok()
        .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        .unwrap_or_else(|| PathBuf::from("."))
        .join(".auth_cache")
}

#[tauri::command]
pub fn update_python_auth_cache(auth_data: AuthData) -> Result<String, String> {
    let cache_path = auth_cache_path();
    
    let auth_cache = AuthCache {
        access_token: auth_data.access_token,
        subscription_status: auth_data.subscription_status,
        user_id: auth_data.user_id,
        last_validated: chrono::Utc::now().to_rfc3339(),
    };
    
    let content = serde_json::to_string_pretty(&auth_cache)
        .map_err(|e| format!("Failed to serialize auth cache: {}", e))?;
    
    if let Some(parent) = cache_path.parent() { let _ = fs::create_dir_all(parent); }

    fs::write(&cache_path, content)
        .map_err(|e| format!("Failed to write auth cache file: {}", e))?;
    
    Ok("Auth cache updated successfully".to_string())
}

#[tauri::command]
pub fn clear_python_auth_cache() -> Result<String, String> {
    let cache_path = auth_cache_path();
    
    if cache_path.exists() {
        fs::remove_file(&cache_path)
            .map_err(|e| format!("Failed to remove auth cache file: {}", e))?;
        Ok("Auth cache cleared successfully".to_string())
    } else {
        Ok("Auth cache file not found".to_string())
    }
}
