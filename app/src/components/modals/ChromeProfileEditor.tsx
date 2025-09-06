import { useState } from 'react'
import { ChromeProfile } from '../../types'
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

interface ChromeProfileEditorProps {
  profile?: ChromeProfile
  profileIndex?: number
  onAdd: (profile: ChromeProfile) => void
  onUpdate: (index: number, profile: ChromeProfile) => void
}

export const ChromeProfileEditor: React.FC<ChromeProfileEditorProps> = ({
  profile,
  profileIndex,
  onAdd,
  onUpdate,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingProfile, setEditingProfile] = useState<ChromeProfile>(
    profile || { name: '', shortcut_path: '' },
  )

  const handleSave = () => {
    if (profile && profileIndex !== undefined) {
      onUpdate(profileIndex, editingProfile)
    } else {
      onAdd(editingProfile)
    }
    setDialogOpen(false)
    setEditingProfile({ name: '', shortcut_path: '' })
  }

  const handleBrowsePath = async () => {
    try {
      const selected = await open({
        filters: [{ name: 'Shortcuts', extensions: ['lnk'] }],
        multiple: false,
      })
      if (typeof selected === 'string') {
        setEditingProfile({ ...editingProfile, shortcut_path: selected })
      }
    } catch (error) {
      console.error('Failed to open file browser:', error)
    }
  }

  return (
    <>
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogTrigger asChild>
          <Button variant={profile ? 'outline' : 'default'} size="sm">
            {profile ? (
              <Edit className="w-4 h-4 mr-2" />
            ) : (
              <Plus className="w-4 h-4 mr-2" />
            )}
            {profile ? 'Edit' : 'Add'} Profile
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {profile ? 'Edit Chrome Profile' : 'Add Chrome Profile'}
            </DialogTitle>
            <DialogDescription>
              Configure a Chrome browser profile with its shortcut path
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            {/* Profile Name */}
            <div className="space-y-2">
              <Label htmlFor="profile-name">Profile Name</Label>
              <Input
                id="profile-name"
                value={editingProfile.name}
                onChange={(e) =>
                  setEditingProfile({ ...editingProfile, name: e.target.value })
                }
                placeholder="Enter profile name..."
              />
            </div>

            {/* Shortcut Path */}
            <div className="space-y-2">
              <Label htmlFor="shortcut-path">Shortcut Path</Label>
              <div className="flex gap-2">
                <Input
                  id="shortcut-path"
                  value={editingProfile.shortcut_path}
                  onChange={(e) =>
                    setEditingProfile({
                      ...editingProfile,
                      shortcut_path: e.target.value,
                    })
                  }
                  placeholder="C:\path\to\chrome-shortcut.lnk"
                  className="flex-1"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleBrowsePath}
                  title="Browse for Chrome shortcut file"
                >
                  <FolderOpen className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Path to the Chrome shortcut file (.lnk) - typically found in
                Desktop or Start Menu
              </p>
            </div>

            {/* Save/Cancel Buttons */}
            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleSave}
                className="flex-1"
                disabled={
                  !editingProfile.name.trim() ||
                  !editingProfile.shortcut_path.trim()
                }
              >
                {profile ? 'Update' : 'Create'} Profile
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
