import { useState } from 'react'
import { CustomApp } from '../../types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Plus, Edit, FolderOpen } from 'lucide-react'
import { open } from '@tauri-apps/plugin-dialog'

interface CustomAppEditorProps {
  app?: CustomApp
  appIndex?: number
  onAdd: (app: CustomApp) => void
  onUpdate: (index: number, app: CustomApp) => void
}

export const CustomAppEditor: React.FC<CustomAppEditorProps> = ({
  app,
  appIndex,
  onAdd,
  onUpdate,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingApp, setEditingApp] = useState<CustomApp>(
    app || { name: '', exe_path: '' },
  )

  const handleSave = () => {
    if (app && appIndex !== undefined) {
      onUpdate(appIndex, editingApp)
    } else {
      onAdd(editingApp)
    }
    setDialogOpen(false)
    setEditingApp({ name: '', exe_path: '' })
  }

  const handleBrowsePath = async () => {
    try {
      const selected = await open({
        filters: [{ name: 'Executables', extensions: ['exe'] }],
        multiple: false,
      })
      if (typeof selected === 'string') {
        setEditingApp({ ...editingApp, exe_path: selected })
      }
    } catch (error) {
      console.error('Failed to open file browser:', error)
    }
  }

  return (
    <>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogTrigger asChild>
          <Button variant={app ? 'outline' : 'default'} size="sm">
            {app ? (
              <Edit className="w-4 h-4 mr-2" />
            ) : (
              <Plus className="w-4 h-4 mr-2" />
            )}
            {app ? 'Edit' : 'Add'} App
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {app ? 'Edit Custom App' : 'Add Custom App'}
            </DialogTitle>
            <DialogDescription>
              Configure a custom app with its executable path
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* App Name */}
            <div className="space-y-2">
              <Label htmlFor="app-name">App Name</Label>
              <Input
                id="app-name"
                value={editingApp.name}
                onChange={(e) =>
                  setEditingApp({ ...editingApp, name: e.target.value })
                }
                placeholder="Enter app name..."
              />
            </div>

            {/* Executable Path */}
            <div className="space-y-2">
              <Label htmlFor="exe-path">Executable Path</Label>
              <div className="flex gap-2">
                <Input
                  id="exe-path"
                  value={editingApp.exe_path}
                  onChange={(e) =>
                    setEditingApp({ ...editingApp, exe_path: e.target.value })
                  }
                  placeholder="C:\\path\\to\\app.exe"
                  className="flex-1"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleBrowsePath}
                  title="Browse for executable file"
                >
                  <FolderOpen className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Path to the application executable (.exe)
              </p>
            </div>
            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleSave}
                className="flex-1"
                disabled={
                  !editingApp.name.trim() || !editingApp.exe_path.trim()
                }
              >
                {app ? 'Update' : 'Create'} App
              </Button>
              <Button
                variant="outline"
                onClick={() => setDialogOpen(false)}
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
