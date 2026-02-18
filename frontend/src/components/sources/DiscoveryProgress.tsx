import { useEffect, useState, useRef } from 'react';
import { useTranslations } from 'next-intl';

interface DiscoveryProgressProps {
  pyramidId?: string;
  onFinish: (count: number) => void;
  onError: (error: string) => void;
}

interface LogEntry {
  message: string;
  level: 'info' | 'warning' | 'error';
  timestamp: string;
}

export default function DiscoveryProgress({ pyramidId, onFinish, onError }: DiscoveryProgressProps) {
  const t = useTranslations('Sources.discovery');
  const [stage, setStage] = useState<string>('pending');
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [progress, setProgress] = useState<{ current: number; total: number; percentage: number; message: string } | null>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Construct URL with query parameters
    const url = new URL('/api/v1/sources/discover/stream', window.location.origin);
    if (pyramidId) {
      url.searchParams.append('pyramid_id', pyramidId);
    }
    
    // Add token if needed (assuming token is in localStorage or handled by cookies)
    // For now, we assume cookie auth or no auth.
    
    const eventSource = new EventSource(url.toString());

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // The payload itself is the data, no outer "data" wrapper unless we wrapped it in backend.
        // Backend yields: `data: {event: ..., data: ...}\n\n`
        // So event.data is the JSON string.
        
        const { event: eventType, data: payload } = data;

        if (eventType === 'stage_update') {
          setStage(payload.stage);
          // Add stage change to logs
          setLogs(prev => [...prev, { 
            message: `Stage: ${payload.label || payload.stage} (${payload.status})`, 
            level: 'info', 
            timestamp: new Date().toISOString() 
          }]);
        } else if (eventType === 'log') {
          setLogs(prev => [...prev, { ...payload, timestamp: new Date().toISOString() }]);
        } else if (eventType === 'progress') {
          setProgress(payload);
        } else if (eventType === 'result') {
          onFinish(payload.count);
          eventSource.close();
        } else if (eventType === 'finish') {
          eventSource.close();
        } else if (eventType === 'error') {
          onError(payload.message);
          eventSource.close();
        }
      } catch (e) {
        console.error('Error parsing SSE data:', e);
      }
    };

    eventSource.onerror = (e) => {
      console.error('SSE error:', e);
      // Only treat as error if it's not a normal close (readyState 2 = CLOSED)
      if (eventSource.readyState !== 2) {
          onError('Connection interrupted');
      }
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [pyramidId, onFinish, onError]);

  // Auto-scroll logs
  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="space-y-6 p-6 border rounded-xl bg-white dark:bg-gray-800 shadow-sm">
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">{t('title')}</h3>
      
      {/* Steps Visualization */}
      <div className="relative flex justify-between">
        <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-200 -z-10 transform -translate-y-1/2 dark:bg-gray-700"></div>
        {['extract', 'search', 'filter', 'proposal'].map((s, index) => {
          const isActive = stage === s;
          const stages = ['extract', 'search', 'filter', 'proposal', 'finish'];
          const currentIndex = stages.indexOf(stage);
          const isCompleted = currentIndex > index || stage === 'finish';
          
          return (
            <div key={s} className="flex flex-col items-center bg-white dark:bg-gray-800 px-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-2 transition-all duration-300
                ${isActive ? 'bg-blue-600 text-white ring-4 ring-blue-100 dark:ring-blue-900' : 
                  isCompleted ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500 dark:bg-gray-700'}`}>
                {isCompleted ? (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </div>
              <span className={`text-xs font-medium ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500'}`}>
                {t(`stages.${s}`)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Progress Bar */}
      {progress && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>{progress.message}</span>
            <span>{Math.round(progress.percentage)}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2 dark:bg-gray-700 overflow-hidden">
            <div className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out" 
                 style={{ width: `${progress.percentage}%` }}></div>
          </div>
        </div>
      )}

      {/* Logs */}
      <div className="space-y-2">
        <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">{t('logs')}</div>
        <div 
            ref={logContainerRef}
            className="h-48 overflow-y-auto bg-gray-900 text-green-400 p-3 rounded-lg text-xs font-mono border border-gray-800 shadow-inner"
        >
            {logs.length === 0 ? (
                <div className="h-full flex items-center justify-center text-gray-600 italic">
                    Initializing discovery process...
                </div>
            ) : (
                logs.map((log, i) => (
                <div key={i} className="mb-1.5 last:mb-0 break-words">
                    <span className="text-gray-500 mr-2">[{new Date(log.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' })}]</span>
                    <span className={log.level === 'error' ? 'text-red-400' : log.level === 'warning' ? 'text-yellow-400' : 'text-gray-300'}>
                    {log.message}
                    </span>
                </div>
                ))
            )}
        </div>
      </div>
    </div>
  );
}
