import { useCallback } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { CustomApp } from '../types'
import { toast } from 'sonner'

export function useCustomApps(loadSettings: () => Promise<void>) {
  const addCustomApp = useCallback(
    async (app: CustomApp) => {
      try {
        await invoke('add_custom_app', { app })
        await loadSettings()
        toast.success('Custom app added')
      } catch (error) {
        toast.error('Failed to add custom app')
        console.error('Failed to add custom app:', error)
      }
    },
    [loadSettings],
  )

  const updateCustomApp = useCallback(
    async (index: number, app: CustomApp) => {
      try {
        await invoke('update_custom_app', { index, app })
        await loadSettings()
        toast.success('Custom app updated')
      } catch (error) {
        toast.error('Failed to update custom app')
        console.error('Failed to update custom app:', error)
      }
    },
    [loadSettings],
  )

  const removeCustomApp = useCallback(
    async (index: number) => {
      try {
        await invoke('remove_custom_app', { index })
        await loadSettings()
        toast.success('Custom app removed')
      } catch (error) {
        toast.error('Failed to remove custom app')
        console.error('Failed to remove custom app:', error)
      }
    },
    [loadSettings],
  )

  return { addCustomApp, updateCustomApp, removeCustomApp }
}
