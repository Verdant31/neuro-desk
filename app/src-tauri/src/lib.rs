mod health;
mod models;
mod settings;
mod startup;
mod auth;
mod logs;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .on_window_event(|_window, event| match event {
            tauri::WindowEvent::CloseRequested { .. } => {
                // Spawn async cleanup on close without blocking UI
                tauri::async_runtime::spawn(async {
                    let _ = health::cleanup_unfinished_scripts().await;
                });
            }
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            settings::load_settings,
            settings::save_settings,
            settings::add_execution_plan,
            settings::update_execution_plan,
            settings::remove_execution_plan,
            settings::add_chrome_profile,
            settings::add_custom_app,
            settings::update_custom_app,
            settings::update_chrome_profile,
            settings::remove_chrome_profile,
            health::get_health_status,
            health::stop_assistant,
            health::cleanup_unfinished_scripts,
            startup::set_startup_enabled,
            startup::is_startup_enabled,
            auth::update_python_auth_cache,
            auth::clear_python_auth_cache,
            logs::tail_os_logs,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
