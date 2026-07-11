import { Key, X, AlertCircle } from 'lucide-react'
import { useApiStore } from '@/stores/apiStore'
import { Button } from '@/components/ui/button'

export function ApiKeySelector() {
  const { activeApiKey, activeKeyName, setActiveApiKey } = useApiStore()

  if (!activeApiKey) {
    return (
      <div className="px-4 mb-6">
        <div className="p-3 rounded-lg border border-dashed border-[var(--border-subtle)] bg-[var(--bg-subtle)]/50">
          <div className="flex items-center gap-2 text-orange-500 mb-2">
            <AlertCircle className="h-3.5 w-3.5" />
            <span className="text-[10px] font-bold uppercase tracking-wider">No active key</span>
          </div>
          <p className="text-[10px] text-[var(--text-muted)] leading-relaxed mb-3">
            Jobs and webhooks require an API key to view.
          </p>
          <Button 
            variant="outline" 
            size="sm" 
            className="w-full h-7 text-[10px] uppercase tracking-wider font-bold"
            onClick={() => window.location.href = '/dashboard/keys'}
          >
            Go to Keys
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 mb-6">
      <div className="p-3 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-card)] shadow-sm relative group">
        <div className="flex items-center gap-2 text-brand mb-1">
          <Key className="h-3.5 w-3.5" />
          <span className="text-[10px] font-bold uppercase tracking-wider">Active Context</span>
        </div>
        <div className="min-w-0">
          <p className="text-xs font-semibold text-[var(--text-primary)] truncate">
            {activeKeyName || 'Unnamed Key'}
          </p>
          <p className="text-[10px] font-mono text-[var(--text-muted)] truncate mt-0.5">
            {activeApiKey.substring(0, 8)}••••••••
          </p>
        </div>
        
        <button 
          onClick={() => setActiveApiKey(null, null)}
          className="absolute top-2 right-2 p-1 rounded-md hover:bg-[var(--bg-subtle)] text-[var(--text-muted)] opacity-0 group-hover:opacity-100 transition-opacity"
          title="Clear active key"
        >
          <X className="h-3 w-3" />
        </button>
      </div>
    </div>
  )
}
