#[cfg(target_os = "windows")]
use winreg::enums::*;
#[cfg(target_os = "windows")]
use winreg::RegKey;

#[tauri::command]
pub fn set_startup_enabled(enable: bool) -> Result<(), String> {
    #[cfg(target_os = "windows")]
    {
        let app_name = "OSAssistant";
        let hkcu = RegKey::predef(HKEY_CURRENT_USER);
        let run = hkcu
            .open_subkey_with_flags(
                "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                KEY_WRITE | KEY_READ,
            )
            .map_err(|e| format!("Failed to open registry key: {}", e))?;

        if enable {
            let sidecar_path = get_sidecar_path()?;
            run.set_value(app_name, &sidecar_path)
                .map_err(|e| format!("Failed to set registry value: {}", e))?;
        } else {
            run.delete_value(app_name).ok();
        }
        Ok(())
    }
    #[cfg(not(target_os = "windows"))]
    {
        Err("Startup management is only supported on Windows".to_string())
    }
}

#[tauri::command]
pub fn is_startup_enabled() -> Result<bool, String> {
    #[cfg(target_os = "windows")]
    {
        let app_name = "OSAssistant";
        let hkcu = RegKey::predef(HKEY_CURRENT_USER);
        let run = hkcu
            .open_subkey_with_flags(
                "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                KEY_READ,
            )
            .map_err(|e| format!("Failed to open registry key: {}", e))?;

        match run.get_value::<String, _>(app_name) {
            Ok(_) => Ok(true),
            Err(_) => Ok(false),
        }
    }
    #[cfg(not(target_os = "windows"))]
    {
        Ok(false)
    }
}

#[cfg(target_os = "windows")]
fn get_sidecar_path() -> Result<String, String> {
    let app_dir = std::env::current_exe()
        .map_err(|e| format!("Failed to get executable path: {}", e))?
        .parent()
        .ok_or("Failed to get executable directory")?
        .to_path_buf();

    let candidates = [
        app_dir.join("main.exe"),
        app_dir.join("main"), // if extensionless
        app_dir.join("resources").join("main.exe"),
        app_dir.join("resources").join("main"),
    ];

    if let Some(found) = candidates.iter().find(|p| p.exists()) {
        return Ok(found.to_string_lossy().to_string());
    }

    let mut found: Option<std::path::PathBuf> = None;
    for dir in [app_dir.clone(), app_dir.join("resources")].iter() {
        if let Ok(entries) = std::fs::read_dir(dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if let Some(name) = path.file_name().and_then(|s| s.to_str()) {
                    if name.starts_with("main-") && name.ends_with(".exe") && path.is_file() {
                        found = Some(path);
                        break;
                    }
                }
            }
        }
        if found.is_some() { break; }
    }

    if let Some(p) = found { return Ok(p.to_string_lossy().to_string()); }

    Err("Sidecar executable 'main' not found in expected locations".to_string())
}
