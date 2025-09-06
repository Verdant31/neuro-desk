use std::env;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::PathBuf;

#[derive(serde::Serialize)]
pub struct LogChunk {
    pub content: String,
    pub offset: u64,
    pub path: String,
}

fn resources_base_dir() -> Option<PathBuf> {
    // Try the Tauri bundle layout first: <exe_dir>/resources
    if let Ok(exe) = env::current_exe() {
        if let Some(dir) = exe.parent() {
            let candidate = dir.join("resources");
            if candidate.exists() {
                return Some(candidate);
            }
        }
    }

    // Fallbacks for dev:
    // - current working directory ./resources
    // - <cwd>/src-tauri/resources (typical repo layout)
    if let Ok(cwd) = env::current_dir() {
        let candidate = cwd.join("resources");
        if candidate.exists() {
            return Some(candidate);
        }
        let candidate = cwd.join("src-tauri").join("resources");
        if candidate.exists() {
            return Some(candidate);
        }
    }

    None
}

fn resolve_log_path() -> Option<PathBuf> {
    let base = resources_base_dir()?;
    let candidate1 = base.join("logs").join("os_assistant.log");
    if candidate1.exists() {
        return Some(candidate1);
    }
    let candidate2 = base.join("os_assistant.log");
    if candidate2.exists() {
        return Some(candidate2);
    }
    // If not found, still prefer the logs folder path for consistency
    Some(base.join("logs").join("os_assistant.log"))
}

#[tauri::command]
pub fn tail_os_logs(
    offset: Option<u64>,
    max_bytes: Option<u64>,
    last_lines: Option<usize>,
) -> Result<LogChunk, String> {
    let path = resolve_log_path().ok_or_else(|| "resources directory not found".to_string())?;

    // If the file does not exist yet, return empty chunk with offset 0
    if !path.exists() {
        return Ok(LogChunk {
            content: String::new(),
            offset: 0,
            path: path.to_string_lossy().to_string(),
        });
    }

    let mut file = File::open(&path)
        .map_err(|e| format!("Failed to open log file {}: {}", path.display(), e))?;

    let len = file
        .metadata()
        .map_err(|e| format!("Failed to stat log file: {}", e))?
        .len();

    let cap = max_bytes.unwrap_or(64 * 1024); // 64 KiB default cap per request
    let mut start = offset.unwrap_or(0);

    // Handle truncation/rotation: if the file shrank, reset to the tail within cap
    if start > len {
        start = len.saturating_sub(cap);
    }

    // If the gap is larger than cap, only return the last `cap` bytes to avoid huge payloads
    // If the caller requests only the last N lines and we are at offset 0, optimize by tailing from the end
    if last_lines.unwrap_or(0) > 0 && start == 0 {
        let to_read = len.min(cap);
        let read_start = len.saturating_sub(to_read);
        file
            .seek(SeekFrom::Start(read_start))
            .map_err(|e| format!("Failed to seek log file: {}", e))?;
        let mut buf = String::new();
        file
            .read_to_string(&mut buf)
            .map_err(|e| format!("Failed to read log file: {}", e))?;
        let mut norm = buf.replace('\r', "");
        // Keep only the last N lines
        let n = last_lines.unwrap_or(10);
        let parts: Vec<&str> = norm.split('\n').collect();
        let take_from = parts.len().saturating_sub(n);
        let content = parts[take_from..].join("\n");
        // If read started mid-line, ensure we don't start with a broken first line
        if read_start > 0 {
            if let Some(idx) = content.find('\n') {
                norm = content[idx + 1..].to_string();
            } else {
                norm = String::new();
            }
        } else {
            norm = content;
        }
        return Ok(LogChunk {
            content: norm,
            offset: len,
            path: path.to_string_lossy().to_string(),
        });
    }

    let available = len.saturating_sub(start);
    let to_read = available.min(cap);

    // Seek to the requested start (adjusted) and read up to `to_read` bytes only
    file
        .seek(SeekFrom::Start(start))
        .map_err(|e| format!("Failed to seek log file: {}", e))?;

    let mut buf = String::new();
    {
        use std::io::Read as _;
        let mut limited = file.take(to_read);
        limited
            .read_to_string(&mut buf)
            .map_err(|e| format!("Failed to read log file: {}", e))?;
    }

    Ok(LogChunk {
        content: buf,
        offset: len,
        path: path.to_string_lossy().to_string(),
    })
}
