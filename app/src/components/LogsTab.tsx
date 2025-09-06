import { useEffect, useRef, useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'

type LogChunk = {
  content: string
  offset: string | number
  path: string
}

export function LogsTab() {
  const [text, setText] = useState<string>('')
  const [path, setPath] = useState<string>('')
  const [paused, setPaused] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const containerRef = useRef<HTMLDivElement>(null)
  const lastUpdateRef = useRef<number>(0)
  const offsetRef = useRef<number>(0)
  const inFlightRef = useRef<boolean>(false)

  const fetchLogs = async () => {
    if (inFlightRef.current) return
    inFlightRef.current = true
    const requestOffset = offsetRef.current
    try {
      const chunk = await invoke<LogChunk>('tail_os_logs', {
        offset: requestOffset,
        maxBytes: 64 * 1024,
        lastLines: requestOffset === 0 ? 10 : undefined,
      })
      const nextOffset =
        typeof chunk.offset === 'string'
          ? parseInt(chunk.offset, 10)
          : (chunk.offset as number)
      setPath(chunk.path)
      if (chunk.content && nextOffset > requestOffset) {
        const now = Date.now()
        const shouldUpdate = now - (lastUpdateRef.current || 0) > 100
        if (shouldUpdate) {
          lastUpdateRef.current = now
          setText((prev) => {
            const merged =
              (prev ? prev + (prev.endsWith('\n') ? '' : '\n') : '') +
              chunk.content.replace(/\r/g, '')
            const CAP = 500_000
            if (merged.length > CAP) {
              const start = Math.floor(merged.length * 0.4)
              const nl = merged.indexOf('\n', start)
              return nl > -1 ? merged.slice(nl + 1) : merged.slice(start)
            }
            return merged
          })
        }
        offsetRef.current = nextOffset
      } else if (nextOffset > offsetRef.current) {
        offsetRef.current = nextOffset
      }
    } catch (e) {
      console.error('Failed to fetch logs:', e)
    } finally {
      inFlightRef.current = false
    }
  }

  useEffect(() => {
    if (paused) return
    const id = setInterval(() => {
      if (!inFlightRef.current) fetchLogs()
    }, 1000)
    fetchLogs()
    return () => clearInterval(id)
  }, [paused])

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [text, autoScroll])

  const clearLogs = () => {
    setText('')
    offsetRef.current = 0
    lastUpdateRef.current = 0
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Logs</h2>
          <p className="text-muted-foreground">
            Acompanhe os logs do OS Assistant em tempo real
          </p>
          {path && (
            <div className="text-xs text-muted-foreground mt-1">
              Arquivo: <span className="font-mono">{path}</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={paused ? 'secondary' : 'default'}>
            {paused ? 'Pausado' : 'Ao vivo'}
          </Badge>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPaused((p) => !p)}
          >
            {paused ? 'Retomar' : 'Pausar'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoScroll((s) => !s)}
          >
            {autoScroll ? 'Auto-scroll: On' : 'Auto-scroll: Off'}
          </Button>
          <Button variant="outline" size="sm" onClick={clearLogs}>
            Limpar
          </Button>
        </div>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Saída</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            ref={containerRef}
            className="h-[420px] overflow-auto rounded bg-muted p-3 font-mono text-xs whitespace-pre-wrap"
          >
            {text.length === 0 ? (
              <div className="text-muted-foreground">Sem conteúdo ainda…</div>
            ) : (
              <pre className="m-0 whitespace-pre-wrap break-words">{text}</pre>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
