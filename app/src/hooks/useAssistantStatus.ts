import { invoke } from '@tauri-apps/api/core'
import { useState, useEffect } from 'react'
import { Command } from '@tauri-apps/plugin-shell'

export interface HealthStatus {
  status: string
  message: string
  timestamp: string
}

export function useAssistantStatus() {
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const checkHealthStatus = async ({
    tries = 3,
    silent = false,
  }: {
    tries?: number
    silent?: boolean
  }) => {
    if (!silent) setLoading(true)
    setError(null)
    try {
      for (let i = 0; i < tries; i++) {
        const status = await invoke<HealthStatus>('get_health_status')
        console.log('Checking status...')
        setHealthStatus(status)
        if (i < 2) {
          await new Promise((resolve) => setTimeout(resolve, 3000))
        }
      }
    } catch (err) {
      setError(err as string)
      console.error('Failed to get health status:', err)
    } finally {
      setLoading(false)
    }
  }

  const startAssistant = async () => {
    try {
      setLoading(true)
      setError(null)
      const command = Command.sidecar('resources/main')
      command.execute()
      await checkHealthStatus({})
    } catch (err) {
      setError(err as string)
      console.error('Failed to start assistant:', err)
    }
  }

  const stopAssistant = async () => {
    try {
      setLoading(true)
      setError(null)
      await invoke<HealthStatus>('stop_assistant')
      await checkHealthStatus({})
    } catch (err) {
      setError(err as string)
      console.error('Failed to stop assistant:', err)
    } finally {
      setLoading(false)
    }
  }

  const cleanupUnfinishedScripts = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await invoke<string>('cleanup_unfinished_scripts')
      console.log('Cleanup result:', result)
    } catch (err) {
      setError(err as string)
      console.error('Failed to cleanup unfinished scripts:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (
      healthStatus?.status === 'running' ||
      healthStatus?.status === 'processing' ||
      healthStatus?.status === 'starting'
    ) {
      const interval = setInterval(
        () => checkHealthStatus({ tries: 1, silent: true }),
        5000,
      )
      return () => clearInterval(interval)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [healthStatus?.timestamp])

  useEffect(() => {
    cleanupUnfinishedScripts()
    checkHealthStatus({ tries: 1 })
  }, [])

  return {
    healthStatus,
    loading,
    error,
    checkHealthStatus,
    startAssistant,
    stopAssistant,
    cleanupUnfinishedScripts,
  }
}
