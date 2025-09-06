import { invoke } from '@tauri-apps/api/core'
import { useState, useEffect } from 'react'

export function useStartup() {
  const [isStartupEnabled, setIsStartupEnabled] = useState<boolean>(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const checkStartupStatus = async () => {
    try {
      setLoading(true)
      setError(null)
      const status = await invoke<boolean>('is_startup_enabled')
      setIsStartupEnabled(status)
    } catch (err) {
      setError(err as string)
      console.error('Failed to check startup status:', err)
    } finally {
      setLoading(false)
    }
  }

  const setStartupEnabled = async (enable: boolean) => {
    try {
      setLoading(true)
      setError(null)
      await invoke('set_startup_enabled', { enable })
      setIsStartupEnabled(enable)
    } catch (err) {
      setError(err as string)
      console.error('Failed to set startup status:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkStartupStatus()
  }, [])

  return {
    isStartupEnabled,
    loading,
    error,
    setStartupEnabled,
    checkStartupStatus,
  }
}
