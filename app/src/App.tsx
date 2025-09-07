import { Toaster } from 'sonner'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent } from '@/components/ui/card'
import { Loader2 } from 'lucide-react'
import { useSettings } from './hooks/useSettings'
import { useTheme } from './hooks/useTheme'
import { AppHeader } from '@/components/AppHeader'
import { GeneralSettingsTab } from '@/components/GeneralSettingsTab'
import { ExecutionPlansTab } from '@/components/ExecutionPlansTab'
import { ChromeProfilesTab } from '@/components/ChromeProfilesTab'
import { AboutTab } from '@/components/AboutTab'
import { CustomAppsTab } from '@/components/CustomAppsTab'
import { AssistantStatus } from '@/components/AssistantStatus'
import { LogsTab } from '@/components/LogsTab'
import { useExecutionPlans } from './hooks/useExecutionPlans'
import { useChromeProfiles } from './hooks/useChromeProfiles'
import { useCustomApps } from './hooks/useCustomApps'
import './index.css'

function App() {
  const {
    settings,
    loading,
    saving,
    saveSettings,
    updateSettings,
    loadSettings,
  } = useSettings()

  const { addExecutionPlan, updateExecutionPlan, removeExecutionPlan } =
    useExecutionPlans(loadSettings)

  const { addChromeProfile, updateChromeProfile, removeChromeProfile } =
    useChromeProfiles(loadSettings)
  const { addCustomApp, updateCustomApp, removeCustomApp } =
    useCustomApps(loadSettings)

  const { theme, toggleTheme } = useTheme()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-6">
        <Card className="w-full max-w-sm">
          <CardContent className="flex flex-col items-center justify-center p-8 space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <div className="text-lg font-medium text-center">
              Carregando configurações...
            </div>
            <div className="text-sm text-muted-foreground text-center">
              Preparando a interface
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <Toaster richColors position="top-right" />
      <div className="max-w-6xl mx-auto">
        <AppHeader
          theme={theme}
          toggleTheme={toggleTheme}
          onSave={saveSettings}
          saving={saving}
        />

        <div className="mb-6">
          <AssistantStatus settings={settings} />
        </div>

        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="executionPlans">Execution Plans</TabsTrigger>
            <TabsTrigger value="chrome">Chrome Profiles</TabsTrigger>
            <TabsTrigger value="customApps">Custom Apps</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
            <TabsTrigger value="about">About</TabsTrigger>
          </TabsList>
          <TabsContent value="general" className="space-y-6">
            <GeneralSettingsTab
              settings={settings}
              updateSettings={updateSettings}
            />
          </TabsContent>
          <TabsContent value="executionPlans" className="space-y-6">
            <ExecutionPlansTab
              executionPlans={settings.execution_plans}
              addExecutionPlan={addExecutionPlan}
              updateExecutionPlan={updateExecutionPlan}
              removeExecutionPlan={removeExecutionPlan}
            />
          </TabsContent>
          <TabsContent value="chrome" className="space-y-6">
            <ChromeProfilesTab
              chromeProfiles={settings.chrome_profiles}
              addChromeProfile={addChromeProfile}
              updateChromeProfile={updateChromeProfile}
              removeChromeProfile={removeChromeProfile}
            />
          </TabsContent>
          <TabsContent value="customApps" className="space-y-6">
            <CustomAppsTab
              customApps={settings.custom_apps}
              addCustomApp={addCustomApp}
              updateCustomApp={updateCustomApp}
              removeCustomApp={removeCustomApp}
            />
          </TabsContent>
          <TabsContent value="logs" className="space-y-6">
            <LogsTab />
          </TabsContent>
          <TabsContent value="about" className="space-y-6">
            <AboutTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App
