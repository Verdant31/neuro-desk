import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Trash2 } from 'lucide-react'
import React from 'react'
import { CustomApp } from '../types'
import { CustomAppEditor } from './modals/CustomAppEditor'

interface CustomAppsTabProps {
  customApps: CustomApp[]
  addCustomApp: (app: CustomApp) => void
  updateCustomApp: (index: number, app: CustomApp) => void
  removeCustomApp: (index: number) => void
}

export const CustomAppsTab: React.FC<CustomAppsTabProps> = ({
  customApps,
  addCustomApp,
  updateCustomApp,
  removeCustomApp,
}) => {
  return (
    <>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Custom Apps</h2>
          <p className="text-muted-foreground">
            Add custom applications for voice launching
          </p>
        </div>
        <CustomAppEditor onAdd={addCustomApp} onUpdate={updateCustomApp} />
      </div>
      <div className="grid gap-4">
        {customApps.map((app, index) => (
          <Card key={index}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{app.name}</CardTitle>
                  <CardDescription className="font-mono text-sm">
                    {app.exe_path}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <CustomAppEditor
                    app={app}
                    appIndex={index}
                    onAdd={addCustomApp}
                    onUpdate={updateCustomApp}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeCustomApp(index)}
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
}
