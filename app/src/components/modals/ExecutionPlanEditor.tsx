import { useState } from 'react'
import {
  ExecutionPlan,
  Action,
  ACTION_TYPES,
  POSITIONS,
  MONITOR_ACTIONS,
} from '../../types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Card, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Edit, Trash2 } from 'lucide-react'
import { Switch } from '@/components/ui/switch'

interface ExecutionPlanEditorProps {
  plan?: ExecutionPlan
  planIndex?: number
  onAdd: (plan: ExecutionPlan) => void
  onUpdate: (index: number, plan: ExecutionPlan) => void
}

export const ExecutionPlanEditor: React.FC<ExecutionPlanEditorProps> = ({
  plan,
  planIndex,
  onAdd,
  onUpdate,
}) => {
  const [open, setOpen] = useState(false)
  const [editingPlan, setEditingPlan] = useState<ExecutionPlan>(
    plan || { name: '', actions: [] },
  )
  const [editingAction, setEditingAction] = useState<Action | null>(null)
  const [actionIndex, setActionIndex] = useState<number | null>(null)

  const handleSave = () => {
    if (plan && planIndex !== undefined) {
      onUpdate(planIndex, editingPlan)
    } else {
      onAdd(editingPlan)
    }
    setOpen(false)
    setEditingPlan({ name: '', actions: [] })
  }

  const handleAddAction = () => {
    setEditingAction({
      action_type: 'launch_app',
      target: '',
    })
    setActionIndex(null)
  }

  const handleEditAction = (action: Action, index: number) => {
    setEditingAction({ ...action })
    setActionIndex(index)
  }

  const handleSaveAction = () => {
    if (editingAction) {
      const newActions = [...editingPlan.actions]
      if (actionIndex !== null) {
        newActions[actionIndex] = editingAction
      } else {
        newActions.push(editingAction)
      }
      setEditingPlan({ ...editingPlan, actions: newActions })
      setEditingAction(null)
      setActionIndex(null)
    }
  }

  const handleRemoveAction = (index: number) => {
    const newActions = editingPlan.actions.filter((_, i) => i !== index)
    setEditingPlan({ ...editingPlan, actions: newActions })
  }

  const getActionFields = (action: Action) => {
    const fields = []

    // Target field (common to most actions)
    fields.push(
      <div key="target" className="space-y-2">
        <Label htmlFor="target">Target</Label>
        <Input
          id="target"
          value={action.target || ''}
          onChange={(e) =>
            setEditingAction({ ...action, target: e.target.value })
          }
          placeholder="Application name or path"
        />
      </div>,
    )

    // Position field (for move_window)
    if (action.action_type === 'move_window') {
      fields.push(
        <div key="position" className="space-y-2">
          <Label htmlFor="position">Position</Label>
          <Select
            value={action.position || ''}
            onValueChange={(value) =>
              setEditingAction({ ...action, position: value })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select position" />
            </SelectTrigger>
            <SelectContent>
              {POSITIONS.map((pos) => (
                <SelectItem key={pos} value={pos}>
                  {pos}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>,
      )
    }

    // Monitor index field (for move_window, split_screen, monitor_control)
    if (
      ['move_window', 'split_screen', 'monitor_control'].includes(
        action.action_type,
      )
    ) {
      fields.push(
        <div key="monitor_index" className="space-y-2">
          <Label htmlFor="monitor_index">Monitor Index</Label>
          <Input
            id="monitor_index"
            type="number"
            value={action.monitor_index?.toString() || ''}
            onChange={(e) =>
              setEditingAction({
                ...action,
                monitor_index: e.target.value
                  ? parseInt(e.target.value)
                  : undefined,
              })
            }
            placeholder="0"
          />
        </div>,
      )
    }

    // Volume change field (for update_app_volume)
    if (action.action_type === 'update_app_volume') {
      fields.push(
        <div key="volume_change" className="space-y-2">
          <Label htmlFor="volume_change">Volume Change</Label>
          <Input
            id="volume_change"
            type="number"
            value={action.volume_change?.toString() || ''}
            onChange={(e) =>
              setEditingAction({
                ...action,
                volume_change: e.target.value
                  ? parseInt(e.target.value)
                  : undefined,
              })
            }
            placeholder="10"
          />
        </div>,
      )
    }

    // Second app field (for split_screen)
    if (action.action_type === 'split_screen') {
      fields.push(
        <div key="second_app" className="space-y-2">
          <Label htmlFor="second_app">Second App</Label>
          <Input
            id="second_app"
            value={action.second_app || ''}
            onChange={(e) =>
              setEditingAction({ ...action, second_app: e.target.value })
            }
            placeholder="Second application name or path"
          />
        </div>,
      )
    }

    // Monitor action field (for monitor_control)
    if (action.action_type === 'monitor_control') {
      fields.push(
        <div key="monitor_action" className="space-y-2">
          <Label htmlFor="monitor_action">Action</Label>
          <Select
            value={action.monitor_action || ''}
            onValueChange={(value) =>
              setEditingAction({ ...action, monitor_action: value })
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Select action" />
            </SelectTrigger>
            <SelectContent>
              {MONITOR_ACTIONS.map((act) => (
                <SelectItem key={act} value={act}>
                  {act}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>,
      )
    }

    return fields
  }

  return (
    <>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button variant={plan ? 'outline' : 'default'} size="sm">
            {plan ? (
              <Edit className="w-4 h-4 mr-2" />
            ) : (
              <Plus className="w-4 h-4 mr-2" />
            )}
            {plan ? 'Edit' : 'Add'} Plan
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {plan ? 'Edit Execution Plan' : 'Add Execution Plan'}
            </DialogTitle>
            <DialogDescription>
              Configure the execution plan and its associated actions
            </DialogDescription>
          </DialogHeader>
          {/* Add run_on_startup toggle here */}
          <div className="flex items-center gap-2 mb-4">
            <Switch
              id="run_on_startup"
              checked={!!editingPlan.run_on_startup}
              onCheckedChange={(checked) =>
                setEditingPlan((prev) => ({ ...prev, run_on_startup: checked }))
              }
            />
            <Label htmlFor="run_on_startup">Run on startup</Label>
          </div>

          <div className="space-y-6">
            {/* Plan Name */}
            <div className="space-y-2">
              <Label htmlFor="plan-name">Plan Name</Label>
              <Input
                id="plan-name"
                value={editingPlan.name}
                onChange={(e) =>
                  setEditingPlan({ ...editingPlan, name: e.target.value })
                }
                placeholder="Enter plan name..."
              />
            </div>

            {/* Actions List */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Actions</h3>
                <Button onClick={handleAddAction} size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Action
                </Button>
              </div>

              {editingPlan.actions.map((action, index) => (
                <Card key={index}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">
                        {action.action_type}
                        {action.target && ` → ${action.target}`}
                      </CardTitle>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditAction(action, index)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleRemoveAction(index)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              ))}

              {editingPlan.actions.length === 0 && (
                <p className="text-muted-foreground text-center py-4">
                  No actions configured. Click {'Add Action'} to get started.
                </p>
              )}
            </div>

            {/* Action Editor Dialog */}
            {editingAction && (
              <Dialog
                open={!!editingAction}
                onOpenChange={() => setEditingAction(null)}
              >
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>
                      {actionIndex !== null ? 'Edit Action' : 'Add Action'}
                    </DialogTitle>
                  </DialogHeader>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="action-type">Action Type</Label>
                      <Select
                        value={editingAction.action_type}
                        onValueChange={(value) =>
                          setEditingAction({
                            ...editingAction,
                            action_type: value,
                          })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {ACTION_TYPES.map((type) => (
                            <SelectItem key={type} value={type}>
                              {type.replace(/_/g, ' ')}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {getActionFields(editingAction)}

                    <div className="flex gap-2">
                      <Button onClick={handleSaveAction} className="flex-1">
                        Save Action
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => setEditingAction(null)}
                        className="flex-1"
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                </DialogContent>
              </Dialog>
            )}

            {/* Save/Cancel Buttons */}
            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleSave}
                className="flex-1"
                disabled={!editingPlan.name.trim()}
              >
                {plan ? 'Update' : 'Create'} Plan
              </Button>
              <Button
                variant="outline"
                onClick={() => setOpen(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}
