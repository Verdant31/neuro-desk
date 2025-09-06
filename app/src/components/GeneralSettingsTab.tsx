import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import React from 'react'
import { Settings } from '../types'
import { useStartup } from '@/hooks/useStartup'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

interface GeneralSettingsTabProps {
  settings: Settings
  updateSettings: (updates: Partial<Settings>) => void
}

export const GeneralSettingsTab: React.FC<GeneralSettingsTabProps> = ({
  settings,
  updateSettings,
}) => {
  const { isStartupEnabled, loading, setStartupEnabled } = useStartup()

  const handleStartupToggle = async (enabled: boolean) => {
    await setStartupEnabled(enabled)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>General Settings</CardTitle>
        <CardDescription>
          Configure basic assistant settings and paths
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="wake-phrase">Wake Phrase</Label>
            <Input
              id="wake-phrase"
              value={settings.wake_phrase}
              onChange={(e) => updateSettings({ wake_phrase: e.target.value })}
              placeholder="Enter wake phrase..."
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="llm-provider">LLM Provider</Label>
            <Select
              value={settings.llm_provider || 'ollama'}
              onValueChange={(value) =>
                updateSettings({
                  llm_provider: value as Settings['llm_provider'],
                })
              }
            >
              <SelectTrigger id="llm-provider">
                <SelectValue placeholder="Select provider" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ollama">Ollama (local)</SelectItem>
                <SelectItem value="openai">OpenAI (cloud)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {settings.llm_provider === 'openai' && (
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="openai-api-key">OpenAI API Key</Label>
              <Input
                id="openai-api-key"
                type="password"
                value={settings.openai_api_key || ''}
                onChange={(e) =>
                  updateSettings({ openai_api_key: e.target.value })
                }
                placeholder="sk-..."
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="llm-model">Model</Label>
              <Input
                id="llm-model"
                value={settings.llm_model || ''}
                onChange={(e) => updateSettings({ llm_model: e.target.value })}
                placeholder="gpt-4o-mini (default)"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="openai-base-url">
                OpenAI Base URL (opcional)
              </Label>
              <Input
                id="openai-base-url"
                value={settings.openai_base_url || ''}
                onChange={(e) =>
                  updateSettings({ openai_base_url: e.target.value })
                }
                placeholder="https://api.openai.com/v1"
              />
            </div>
          </div>
        )}

        <div className="flex items-center justify-between">
          <div className="space-y-0.5">
            <Label htmlFor="startup-toggle">
              Start Assistant on Windows Startup
            </Label>
            <p className="text-sm text-muted-foreground">
              Automatically start the OS Assistant when Windows boots up
            </p>
          </div>
          <Switch
            id="startup-toggle"
            checked={isStartupEnabled}
            onCheckedChange={handleStartupToggle}
            disabled={loading}
          />
        </div>
      </CardContent>
    </Card>
  )
}
