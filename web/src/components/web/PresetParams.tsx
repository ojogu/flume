import { Plus, Trash2 } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select, SelectTrigger, SelectValue, SelectContent, SelectItem,
} from '@/components/ui/select'
import { useWebStore } from '@/stores/webStore'
import { getOperation, type ParamField } from '@/lib/presets'

function TimecodeInput({
  value,
  onChange,
  placeholder,
  label,
  required,
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  label: string
  required?: boolean
}) {
  return (
    <div className="space-y-1.5">
      <Label>
        {label}
        {required && <span className="text-red-500">*</span>}
      </Label>
      <Input
        placeholder={placeholder ?? '0:00'}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}

function EnumSelect({
  value,
  onChange,
  values,
  label,
  required,
}: {
  value: string
  onChange: (v: string) => void
  values: string[]
  label: string
  required?: boolean
}) {
  return (
    <div className="space-y-1.5">
      <Label>
        {label}
        {required && <span className="text-red-500">*</span>}
      </Label>
      <Select value={value ?? ''} onValueChange={onChange}>
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select..." />
        </SelectTrigger>
        <SelectContent>
          {values.map((v) => (
            <SelectItem key={v} value={v}>{v}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}

function NumberInput({
  value,
  onChange,
  min,
  max,
  label,
  required,
}: {
  value: number | undefined
  onChange: (v: number | undefined) => void
  min?: number
  max?: number
  label: string
  required?: boolean
}) {
  return (
    <div className="space-y-1.5">
      <Label>
        {label}
        {required && <span className="text-red-500">*</span>}
      </Label>
      <Input
        type="number"
        value={value ?? ''}
        min={min}
        max={max}
        onChange={(e) => {
          const v = e.target.value === '' ? undefined : Number(e.target.value)
          onChange(v)
        }}
      />
      {(min !== undefined || max !== undefined) && (
        <p className="text-xs text-[var(--text-muted)]">
          {min !== undefined && max !== undefined
            ? `${min} – ${max}`
            : min !== undefined
              ? `Min: ${min}`
              : `Max: ${max}`}
        </p>
      )}
    </div>
  )
}

function TextInput({
  value,
  onChange,
  placeholder,
  label,
  required,
  type = 'text',
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  label: string
  required?: boolean
  type?: string
}) {
  return (
    <div className="space-y-1.5">
      <Label>
        {label}
        {required && <span className="text-red-500">*</span>}
      </Label>
      <Input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  )
}

function BooleanSwitch({
  value,
  onChange,
  label,
}: {
  value: boolean
  onChange: (v: boolean) => void
  label: string
}) {
  return (
    <div className="flex items-center justify-between">
      <Label>{label}</Label>
      <Switch checked={value} onCheckedChange={onChange} />
    </div>
  )
}

function ArrayField({
  value,
  onChange,
  field,
  label,
  required,
}: {
  value: unknown[]
  onChange: (v: unknown[]) => void
  field: ParamField
  label: string
  required?: boolean
}) {
  const items = Array.isArray(value) ? value : []

  const addItem = () => {
    if (field.items?.type === 'object' && field.items.fields) {
      const obj: Record<string, unknown> = {}
      for (const [k, f] of Object.entries(field.items.fields)) {
        obj[k] = f.default ?? ''
      }
      onChange([...items, obj])
    } else {
      onChange([...items, ''])
    }
  }

  const removeItem = (idx: number) => {
    onChange(items.filter((_, i) => i !== idx))
  }

  const updateItem = (idx: number, val: unknown) => {
    const next = [...items]
    next[idx] = val
    onChange(next)
  }

  return (
    <div className="space-y-2">
      <Label>
        {label}
        {required && <span className="text-red-500">*</span>}
      </Label>
      <div className="space-y-2">
        {items.map((item, idx) => (
          <div key={idx} className="flex gap-2 items-start">
            <div className="flex-1">
              {field.items?.type === 'object' && field.items.fields ? (
                <div className="flex gap-2">
                  {Object.entries(field.items.fields).map(([k, f]) => (
                    <div key={k} className="flex-1">
                      <TimecodeInput
                        value={String((item as Record<string, unknown>)[k] ?? '')}
                        onChange={(v) => {
                          const obj = { ...(item as Record<string, unknown>), [k]: v }
                          updateItem(idx, obj)
                        }}
                        placeholder={f.placeholder}
                        label={k}
                        required={f.required}
                      />
                    </div>
                  ))}
                </div>
              ) : (
                <Input
                  type="url"
                  placeholder={field.items?.placeholder ?? 'https://...'}
                  value={String(item ?? '')}
                  onChange={(e) => updateItem(idx, e.target.value)}
                />
              )}
            </div>
            <button
              onClick={() => removeItem(idx)}
              className="mt-6 p-1.5 hover:bg-[var(--bg-subtle)] rounded"
            >
              <Trash2 className="h-4 w-4 text-[var(--text-muted)]" />
            </button>
          </div>
        ))}
      </div>
      <button
        onClick={addItem}
        className="flex items-center gap-1.5 text-sm text-brand hover:text-[var(--accent-hover)] transition-colors"
      >
        <Plus className="h-4 w-4" />
        Add {label.toLowerCase()}
      </button>
    </div>
  )
}

function ParamFieldRenderer({
  name,
  field,
  value,
  onChange,
}: {
  name: string
  field: ParamField
  value: unknown
  onChange: (v: unknown) => void
}) {
  const label = name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())

  switch (field.type) {
    case 'timecode':
      return (
        <TimecodeInput
          value={String(value ?? '')}
          onChange={onChange}
          placeholder={field.placeholder}
          label={label}
          required={field.required}
        />
      )
    case 'enum':
      return (
        <EnumSelect
          value={String(value ?? '')}
          onChange={onChange}
          values={field.values ?? []}
          label={label}
          required={field.required}
        />
      )
    case 'integer':
    case 'float':
      return (
        <NumberInput
          value={value as number | undefined}
          onChange={onChange}
          min={field.min}
          max={field.max}
          label={label}
          required={field.required}
        />
      )
    case 'boolean':
      return (
        <BooleanSwitch
          value={Boolean(value)}
          onChange={onChange}
          label={label}
        />
      )
    case 'url':
      return (
        <TextInput
          value={String(value ?? '')}
          onChange={onChange}
          placeholder={field.placeholder}
          label={label}
          required={field.required}
          type="url"
        />
      )
    case 'array':
      return (
        <ArrayField
          value={(value as unknown[]) ?? []}
          onChange={onChange}
          field={field}
          label={label}
          required={field.required}
        />
      )
    case 'string':
    default:
      return (
        <TextInput
          value={String(value ?? '')}
          onChange={onChange}
          placeholder={field.placeholder}
          label={label}
          required={field.required}
        />
      )
  }
}

export function PresetParams() {
  const { selectedPreset, presetParams, setPresetParam } = useWebStore()
  if (!selectedPreset) return null

  const op = getOperation(selectedPreset)
  if (!op) return null

  const entries = Object.entries(op.params)
  if (entries.length === 0) {
    return (
      <p className="text-sm text-[var(--text-muted)]">
        No parameters needed for this operation.
      </p>
    )
  }

  return (
    <div className="space-y-4">
      {entries.map(([key, field]) => (
        <ParamFieldRenderer
          key={key}
          name={key}
          field={field}
          value={presetParams[key] ?? field.default}
          onChange={(v) => setPresetParam(key, v)}
        />
      ))}
    </div>
  )
}
