import { useAssistantStatus } from '@/hooks/useAssistantStatus'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Play, RefreshCw, Square } from 'lucide-react'
import { ClipLoader } from 'react-spinners'
export function AssistantStatus() {
  const {
    healthStatus,
    loading,
    error,
    checkHealthStatus,
    startAssistant,
    stopAssistant,
  } = useAssistantStatus()

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-green-500'
      case 'processing':
        return 'bg-blue-500'
      case 'error':
        return 'bg-red-500'
      case 'warning':
        return 'bg-yellow-500'
      case 'stopped':
        return 'bg-gray-500'
      case 'offline':
        return 'bg-gray-400'
      case 'starting':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-400'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running':
        return 'Running'
      case 'processing':
        return 'Processing'
      case 'error':
        return 'Error'
      case 'warning':
        return 'Warning'
      case 'stopped':
        return 'Stopped'
      case 'starting':
        return 'Starting'
      case 'offline':
        return 'Offline'
      default:
        return 'Unknown'
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Assistant Status
          <div className="flex gap-2">
            <Button
              onClick={startAssistant}
              className="w-24 cursor-pointer"
              disabled={
                loading ||
                healthStatus?.status === 'running' ||
                healthStatus?.status === 'starting'
              }
            >
              {!loading ? (
                <Play className="h-4 w-4 " />
              ) : (
                <ClipLoader size="16px" color="black" />
              )}
              <p className="ml-2">Start</p>
            </Button>
            <Button
              variant="destructive"
              onClick={stopAssistant}
              className="w-24 cursor-pointer"
              disabled={
                loading ||
                healthStatus?.status === 'stopped' ||
                healthStatus?.status === 'offline'
              }
            >
              <Square className="h-4 w-4 " />

              <p className="ml-1">Stop</p>
            </Button>
            <Button
              variant="outline"
              onClick={() => checkHealthStatus({ tries: 1 })}
              className="w-24 cursor-pointer"
              disabled={loading}
            >
              <RefreshCw
                className={`h-4 w-4  ${loading ? 'animate-spin' : ''}`}
              />
              <p className="ml-1">Refresh</p>
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {healthStatus ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Badge
                className={`${getStatusColor(healthStatus.status)} text-white`}
              >
                {getStatusText(healthStatus.status)}
              </Badge>
            </div>

            <p className="text-sm text-gray-500">{healthStatus.message}</p>

            <p className="text-xs text-gray-500">
              Last updated:{' '}
              {new Date(Number(healthStatus.timestamp) * 1000).toLocaleString()}
            </p>
          </div>
        ) : (
          <p className="text-gray-500 text-sm">
            {loading ? 'Checking status...' : 'No status information available'}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
