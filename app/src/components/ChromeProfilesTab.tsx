import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Trash2 } from 'lucide-react'
import React from 'react'
import { ChromeProfile } from '../types'
import { ChromeProfileEditor } from './modals/ChromeProfileEditor'

interface ChromeProfilesTabProps {
  chromeProfiles: ChromeProfile[]
  addChromeProfile: (profile: ChromeProfile) => void
  updateChromeProfile: (index: number, profile: ChromeProfile) => void
  removeChromeProfile: (index: number) => void
}

export const ChromeProfilesTab: React.FC<ChromeProfilesTabProps> = ({
  chromeProfiles,
  addChromeProfile,
  updateChromeProfile,
  removeChromeProfile,
}) => (
  <>
    <div className="flex items-center justify-between">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Chrome Profiles</h2>
        <p className="text-muted-foreground">
          Manage Chrome browser profiles for quick access
        </p>
      </div>
      <ChromeProfileEditor
        onAdd={addChromeProfile}
        onUpdate={updateChromeProfile}
      />
    </div>
    <div className="grid gap-4">
      {chromeProfiles.map((profile, index) => (
        <Card key={index}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{profile.name}</CardTitle>
                <CardDescription className="font-mono text-sm">
                  {profile.shortcut_path}
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <ChromeProfileEditor
                  profile={profile}
                  profileIndex={index}
                  onAdd={addChromeProfile}
                  onUpdate={updateChromeProfile}
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => removeChromeProfile(index)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>
      ))}
    </div>
  </>
)
