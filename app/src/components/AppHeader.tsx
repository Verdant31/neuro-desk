import { Button } from '@/components/ui/button'
import { Sun, Moon, Save, Play } from 'lucide-react'
import React from 'react'

interface AppHeaderProps {
  theme: string
  toggleTheme: () => void
  onSave: () => void
  saving: boolean
}

export const AppHeader: React.FC<AppHeaderProps> = ({
  theme,
  toggleTheme,
  onSave,
  saving,
}) => {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          OS Assistant Settings
        </h1>
        <p className="text-muted-foreground">
          Configure your voice assistant and automation settings
        </p>
      </div>
      <div className="flex gap-2 items-center">
        <Button
          variant="ghost"
          size="icon"
          aria-label="Toggle dark mode"
          onClick={toggleTheme}
          className="mr-2"
        >
          {theme === 'dark' ? (
            <Sun className="w-5 h-5" />
          ) : (
            <Moon className="w-5 h-5" />
          )}
        </Button>
        <Button onClick={onSave} disabled={saving}>
          <Save className="w-4 h-4 mr-2" />
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
        <Button variant="outline">
          <Play className="w-4 h-4 mr-2" />
          Start Assistant
        </Button>
      </div>
    </div>
  )
}
