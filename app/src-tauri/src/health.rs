use crate::models::HealthStatus;
use serde_json::Value;
use std::io::Read;
use std::io::Write;
use std::net::{TcpStream, ToSocketAddrs};
use std::time::{Duration, SystemTime, UNIX_EPOCH};

#[tauri::command]
pub async fn get_health_status() -> Result<HealthStatus, String> {
    // Execute potentially blocking I/O on a background thread
    let res = tauri::async_runtime::spawn_blocking(|| get_health_status_http()).await;

    match res {
        Ok(Ok(health_status)) => Ok(health_status),
        // If HTTP endpoint is not available or the task failed, return offline status
        _ => Ok(HealthStatus {
            status: "offline".to_string(),
            message: "OS Assistant not started".to_string(),
            timestamp: SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs()
                .to_string(),
        }),
    }
}

fn get_health_status_http() -> Result<HealthStatus, String> {
    // Resolve address and connect with a short timeout to avoid blocking the UI
    let addr = "127.0.0.1:5002"
        .to_socket_addrs()
        .map_err(|e| format!("Failed to resolve address: {}", e))?
        .next()
        .ok_or_else(|| "No address resolved".to_string())?;

    let mut stream = TcpStream::connect_timeout(&addr, Duration::from_millis(300))
        .map_err(|e| format!("Failed to connect to health server: {}", e))?;

    // Set conservative timeouts to keep operations snappy
    stream
        .set_read_timeout(Some(Duration::from_millis(700)))
        .map_err(|e| format!("Failed to set read timeout: {}", e))?;
    stream
        .set_write_timeout(Some(Duration::from_millis(300)))
        .map_err(|e| format!("Failed to set write timeout: {}", e))?;

    let request = "GET /health HTTP/1.1\r\nHost: 127.0.0.1:5002\r\nConnection: close\r\n\r\n";
    stream
        .write_all(request.as_bytes())
        .map_err(|e| format!("Failed to send HTTP request: {}", e))?;

    let mut response = String::new();
    stream
        .read_to_string(&mut response)
        .map_err(|e| format!("Failed to read HTTP response: {}", e))?;

    // Parse HTTP response
    let parts: Vec<&str> = response.split("\r\n\r\n").collect();
    if parts.len() < 2 {
        return Err("Invalid HTTP response format".to_string());
    }

    let json_str = parts[1];
    let json_value: Value = serde_json::from_str(json_str)
        .map_err(|e| format!("Failed to parse JSON response: {}", e))?;

    let status = json_value["status"]
        .as_str()
        .unwrap_or("unknown")
        .to_string();
    let message = json_value["message"].as_str().unwrap_or("").to_string();
    let timestamp = json_value["timestamp"].as_str().unwrap_or("").to_string();

    Ok(HealthStatus {
        status,
        message,
        timestamp,
    })
}

#[tauri::command]
pub async fn stop_assistant() -> Result<HealthStatus, String> {
    // Try graceful shutdown via TCP in a background thread with timeouts
    let _ = tauri::async_runtime::spawn_blocking(|| {
        if let Ok(mut addrs) = "127.0.0.1:5001".to_socket_addrs() {
            if let Some(addr) = addrs.next() {
                if let Ok(mut stream) = TcpStream::connect_timeout(&addr, Duration::from_millis(300)) {
                    let _ = stream.set_write_timeout(Some(Duration::from_millis(300)));
                    let _ = stream.write_all(b"shutdown");
                    std::thread::sleep(std::time::Duration::from_millis(300));
                }
            }
        }
    })
    .await;

    get_health_status().await
}

#[tauri::command]
pub async fn cleanup_unfinished_scripts() -> Result<String, String> {
    let output_res = tauri::async_runtime::spawn_blocking(|| {
        std::process::Command::new("taskkill")
            .args(&["/f", "/im", "main.exe"])
            .output()
    })
    .await
    .map_err(|e| format!("Failed to join cleanup task: {:?}", e))?;

    let output = output_res
        .map_err(|e| format!("Failed to kill main.exe processes: {}", e))?;

    if output.status.success() {
        Ok("Successfully cleaned up unfinished scripts".to_string())
    } else {
        Ok("No unfinished scripts found to clean up".to_string())
    }
}
