import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import React from 'react'

export const AboutTab: React.FC = () => (
  <Card>
    <CardHeader>
      <CardTitle>About OS Assistant</CardTitle>
      <CardDescription>
        Voice-controlled automation assistant for Windows
      </CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div>
        <h3 className="font-semibold mb-2">Features</h3>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground">
          <li>Voice command recognition</li>
          <li>Application automation</li>
          <li>Window management</li>
          <li>Volume control</li>
          <li>Monitor management</li>
          <li>Chrome profile switching</li>
        </ul>
      </div>
      <div>
        <h3 className="font-semibold mb-2">Version</h3>
        <p className="text-muted-foreground">1.0.0</p>
      </div>
    </CardContent>
  </Card>
)
