import { useState, useEffect } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Settings } from '../types'
import { toast } from 'sonner'

export function useSettings() {
  const [settings, setSettings] = useState<Settings>({
    wake_phrase: 'ola jarvis',
    ahk_path: 'C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey64.exe',
    execution_plans: [],
    chrome_profiles: [],
    custom_apps: [],
    llm_provider: 'openai',
    llm_model: 'gpt-4o-mini',
    openai_api_key: null,
    openai_base_url: null,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const loadedSettingsRes = await invoke<Settings>('load_settings')
      console.log({ loadedSettingsRes })
      setSettings(loadedSettingsRes)
    } catch (error) {
      console.error('Failed to load settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    setSaving(true)
    try {
      const result = await invoke<{ settings: Settings; path: string }>(
        'save_settings',
        { settings },
      )
      if (result?.path) {
        toast.success(`Configurações salvas em: ${result.path}`)
      } else {
        toast.success('Configurações salvas com sucesso')
      }
    } catch (error) {
      toast.error('Falha ao salvar configurações')
      console.error('Failed to save settings:', error)
    } finally {
      setSaving(false)
    }
  }

  const updateSettings = (updates: Partial<Settings>) => {
    setSettings((prev) => ({ ...prev, ...updates }))
  }

  return {
    settings,
    setSettings,
    loading,
    saving,
    loadSettings,
    saveSettings,
    updateSettings,
  }
}
