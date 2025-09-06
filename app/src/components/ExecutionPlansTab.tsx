import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Trash2 } from 'lucide-react'
import React from 'react'
import { ExecutionPlan } from '../types'
import { ExecutionPlanEditor } from './modals/ExecutionPlanEditor'
import { Badge } from './ui/badge'

interface ExecutionPlansTabProps {
  executionPlans: ExecutionPlan[]
  addExecutionPlan: (plan: ExecutionPlan) => void
  updateExecutionPlan: (index: number, plan: ExecutionPlan) => void
  removeExecutionPlan: (index: number) => void
}

export const ExecutionPlansTab: React.FC<ExecutionPlansTabProps> = ({
  executionPlans,
  addExecutionPlan,
  updateExecutionPlan,
  removeExecutionPlan,
}) => (
  <>
    <div className="flex items-center justify-between">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Execution Plans</h2>
        <p className="text-muted-foreground">
          Manage execution plans that can be triggered by voice commands
        </p>
      </div>
      <ExecutionPlanEditor
        onAdd={addExecutionPlan}
        onUpdate={updateExecutionPlan}
      />
    </div>
    <div className="grid gap-4">
      {executionPlans.map((plan, index) => (
        <Card key={index}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>
                  {plan.name}{' '}
                  {plan.run_on_startup && (
                    <Badge className="ml-2">Startup</Badge>
                  )}
                </CardTitle>
                <CardDescription>
                  {plan.actions.length} action
                  {plan.actions.length !== 1 ? 's' : ''}
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <ExecutionPlanEditor
                  plan={plan}
                  planIndex={index}
                  onAdd={addExecutionPlan}
                  onUpdate={updateExecutionPlan}
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => removeExecutionPlan(index)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {plan.actions.length === 0 ? (
              <p className="text-muted-foreground">No actions configured</p>
            ) : (
              <div className="space-y-2">
                {plan.actions.map((action, actionIndex) => (
                  <div
                    key={actionIndex}
                    className="flex items-center justify-between p-2 bg-muted rounded"
                  >
                    <div>
                      <span className="font-medium">{action.action_type}</span>
                      {action.target && (
                        <span className="text-muted-foreground ml-2">
                          → {action.target}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  </>
)
