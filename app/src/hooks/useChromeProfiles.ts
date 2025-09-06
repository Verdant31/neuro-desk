import { useCallback } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { ChromeProfile } from '../types'
import { toast } from 'sonner'

export function useChromeProfiles(loadSettings: () => Promise<void>) {
  const addChromeProfile = useCallback(
    async (profile: ChromeProfile) => {
      try {
        await invoke('add_chrome_profile', { profile })
        await loadSettings()
        toast.success('Chrome profile added')
      } catch (error) {
        toast.error('Failed to add chrome profile')
        console.error('Failed to add chrome profile:', error)
      }
    },
    [loadSettings],
  )

  const updateChromeProfile = useCallback(
    async (index: number, profile: ChromeProfile) => {
      try {
        await invoke('update_chrome_profile', { index, profile })
        await loadSettings()
        toast.success('Chrome profile updated')
      } catch (error) {
        toast.error('Failed to update chrome profile')
        console.error('Failed to update chrome profile:', error)
      }
    },
    [loadSettings],
  )

  const removeChromeProfile = useCallback(
    async (index: number) => {
      try {
        await invoke('remove_chrome_profile', { index })
        await loadSettings()
        toast.success('Chrome profile removed')
      } catch (error) {
        toast.error('Failed to remove chrome profile')
        console.error('Failed to remove chrome profile:', error)
      }
    },
    [loadSettings],
  )

  return { addChromeProfile, updateChromeProfile, removeChromeProfile }
}
