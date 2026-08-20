import {
  Scissors, Minimize2, RefreshCw, Maximize2, Droplets,
  Subtitles, VolumeX, MessageSquare, Link as LinkIcon,
  Music, Camera, Image, Download, Check,
} from 'lucide-react'
import { useWebStore } from '@/stores/webStore'
import { OPERATIONS, CATEGORY_LABELS, type OperationDefinition } from '@/lib/presets'
import { cn } from '@/lib/utils'

const ICON_MAP: Record<string, React.ComponentType<{ className?: string }>> = {
  Scissors, Minimize2, RefreshCw, Maximize2, Droplets,
  Subtitles, VolumeX, MessageSquare, Link: LinkIcon,
  Music, Camera, Image, Download,
}

function PresetCard({ op }: { op: OperationDefinition }) {
  const { selectedPreset, selectPreset } = useWebStore()
  const Icon = ICON_MAP[op.icon] ?? Scissors
  const isSelected = selectedPreset === op.name

  return (
    <button
      onClick={() => selectPreset(isSelected ? null : op.name)}
      className={cn(
        'group relative rounded-xl p-5 text-left border transition-all duration-200',
        isSelected
          ? 'border-2 border-[var(--brand)] bg-[var(--brand-light)] shadow-sm'
          : 'border border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--border-strong)] hover:shadow-sm',
      )}
    >
      {isSelected && (
        <div className="absolute top-2.5 right-2.5 h-5 w-5 rounded-full bg-[var(--brand)] flex items-center justify-center">
          <Check className="h-3 w-3 text-white" />
        </div>
      )}
      <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--brand-light)]">
        <Icon className="h-5 w-5 text-brand" />
      </div>
      <h3 className="font-semibold text-[var(--text-primary)] mb-1 text-sm">
        {op.label}
      </h3>
      <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
        {op.description}
      </p>
    </button>
  )
}

export function PresetPicker() {
  const categories = Object.entries(CATEGORY_LABELS)

  return (
    <div className="space-y-6">
      {categories.map(([key, label]) => {
        const ops = OPERATIONS.filter((op) => op.category === key)
        if (ops.length === 0) return null
        return (
          <div key={key}>
            <p className="text-label text-[var(--text-muted)] mb-3">{label}</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {ops.map((op) => (
                <PresetCard key={op.name} op={op} />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
