use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Action {
    pub action_type: String,
    pub target: Option<String>,
    pub position: Option<String>,
    pub monitor_index: Option<i32>,
    pub volume_change: Option<i32>,
    pub second_app: Option<String>,
    pub monitor_action: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ExecutionPlan {
    pub name: String,
    pub actions: Vec<Action>,
    pub run_on_startup: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ChromeProfile {
    pub name: String,
    pub shortcut_path: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CustomApp {
    pub name: String,
    pub exe_path: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    pub wake_phrase: String,
    pub execution_plans: Vec<ExecutionPlan>,
    pub chrome_profiles: Vec<ChromeProfile>,
    pub custom_apps: Vec<CustomApp>,
    #[serde(default = "default_llm_provider")]
    pub llm_provider: String, 
    #[serde(default)]
    pub llm_model: Option<String>,
    #[serde(default)]
    pub openai_api_key: Option<String>,
    #[serde(default)]
    pub openai_base_url: Option<String>,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            wake_phrase: "ola jarvis".to_string(),
            execution_plans: Vec::new(),
            chrome_profiles: Vec::new(),
            custom_apps: Vec::new(),
            llm_provider: default_llm_provider(),
            llm_model: None,
            openai_api_key: None,
            openai_base_url: None,
        }
    }
}

fn default_llm_provider() -> String {
    "ollama".to_string()
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HealthStatus {
    pub status: String,
    pub message: String,
    pub timestamp: String,
}
