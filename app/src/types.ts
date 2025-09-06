export interface Action {
  action_type: string
  target?: string
  position?: string
  monitor_index?: number
  volume_change?: number
  second_app?: string
  monitor_action?: string
}

export interface ExecutionPlan {
  name: string
  actions: Action[]
  run_on_startup?: boolean
}

export interface ChromeProfile {
  name: string
  shortcut_path: string
}

export interface CustomApp {
  name: string
  exe_path: string
}

export interface Settings {
  wake_phrase: string
  ahk_path: string
  execution_plans: ExecutionPlan[]
  chrome_profiles: ChromeProfile[]
  custom_apps: CustomApp[]
  llm_provider?: 'ollama' | 'openai'
  llm_model?: string | null
  openai_api_key?: string | null
  openai_base_url?: string | null
}

export const ACTION_TYPES = [
  'launch_app',
  'move_window',
  'split_screen',
  'close_app',
  'max',
  'min',
  'update_app_volume',
  'monitor_control',
] as const

export const POSITIONS = [
  'Maximized',
  'Top',
  'Bottom',
  'Left',
  'Right',
] as const

export const MONITOR_ACTIONS = ['enable', 'disable'] as const

export interface AuthUser {
  id: string
  aud: string
  role: string
  email: string
  email_confirmed_at: string
  phone: string
  confirmed_at: string
  last_sign_in_at: string
  app_metadata: {
    provider: string
    providers: string[]
  }
  user_metadata: {
    email: string
    email_verified: boolean
    phone_verified: boolean
    sub: string
  }
  identities: Array<{
    identity_id: string
    id: string
    user_id: string
    identity_data: {
      email: string
      email_verified: boolean
      phone_verified: boolean
      sub: string
    }
    provider: string
    last_sign_in_at: string
    created_at: string
    updated_at: string
    email: string
  }>
  created_at: string
  updated_at: string
  is_anonymous: boolean
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  user: AuthUser
  expires_in: number
  token_type: string
  stripe_customer_id: string
  subscription_status: string
}

export interface LoginCredentials {
  email: string
  password: string
}
