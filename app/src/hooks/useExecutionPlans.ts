import { useCallback } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { ExecutionPlan } from '../types'
import { toast } from 'sonner'

export function useExecutionPlans(loadSettings: () => Promise<void>) {
  const addExecutionPlan = useCallback(
    async (plan: ExecutionPlan) => {
      try {
        await invoke('add_execution_plan', { plan })
        await loadSettings()
        toast.success('Execution plan added')
      } catch (error) {
        toast.error('Failed to add execution plan')
        console.error('Failed to add execution plan:', error)
      }
    },
    [loadSettings],
  )

  const updateExecutionPlan = useCallback(
    async (index: number, plan: ExecutionPlan) => {
      try {
        await invoke('update_execution_plan', { index, plan })
        await loadSettings()
        toast.success('Execution plan updated')
      } catch (error) {
        toast.error('Failed to update execution plan')
        console.error('Failed to update execution plan:', error)
      }
    },
    [loadSettings],
  )

  const removeExecutionPlan = useCallback(
    async (index: number) => {
      try {
        await invoke('remove_execution_plan', { index })
        await loadSettings()
        toast.success('Execution plan removed')
      } catch (error) {
        toast.error('Failed to remove execution plan')
        console.error('Failed to remove execution plan:', error)
      }
    },
    [loadSettings],
  )

  return { addExecutionPlan, updateExecutionPlan, removeExecutionPlan }
}
