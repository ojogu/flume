import { useCallback, useRef, useState } from 'react'
import { Upload, Link as LinkIcon, X, FileVideo } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useWebStore } from '@/stores/webStore'
import { uploadFile } from '@/lib/web'
import { cn } from '@/lib/utils'

const MAX_ANON_BYTES = 100 * 1024 * 1024

export function SourceInput() {
  const {
    sourceType,
    sourceUri,
    uploadedFile,
    session,
    setSourceType,
    setSourceUri,
    setUploadedFile,
  } = useWebStore()

  const [isDragging, setIsDragging] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<number | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleUpload = useCallback(
    async (file: File) => {
      if (!session) return
      setUploadError(null)

      if (file.size > MAX_ANON_BYTES) {
        setUploadError('File too large. Maximum for anonymous upload is 100 MB.')
        return
      }

      setUploadProgress(0)
      try {
        const uri = await uploadFile(session.apiKey, file, setUploadProgress)
        setSourceUri(uri)
        setUploadedFile({ name: file.name, size: file.size, type: file.type })
        setUploadProgress(null)
      } catch {
        setUploadError('Upload failed. Please try again.')
        setUploadProgress(null)
      }
    },
    [session, setSourceUri, setUploadedFile],
  )

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleUpload(file)
    },
    [handleUpload],
  )

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleUpload(file)
    },
    [handleUpload],
  )

  const clearFile = () => {
    setSourceUri('')
    setUploadedFile(null)
    setUploadProgress(null)
    setUploadError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-1 rounded-lg bg-[var(--bg-subtle)] p-1">
        <button
          onClick={() => { setSourceType('url'); clearFile() }}
          className={cn(
            'flex-1 flex items-center justify-center gap-2 rounded-md px-4 py-2.5 text-sm font-medium transition-colors',
            sourceType === 'url'
              ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
          )}
        >
          <LinkIcon className="h-4 w-4" />
          URL
        </button>
        <button
          onClick={() => { setSourceType('upload'); setSourceUri('') }}
          className={cn(
            'flex-1 flex items-center justify-center gap-2 rounded-md px-4 py-2.5 text-sm font-medium transition-colors',
            sourceType === 'upload'
              ? 'bg-[var(--bg-card)] text-[var(--text-primary)] shadow-sm'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]',
          )}
        >
          <Upload className="h-4 w-4" />
          Upload
        </button>
      </div>

      {sourceType === 'url' ? (
        <div className="space-y-2">
          <Label htmlFor="source-url">Video URL</Label>
          <Input
            id="source-url"
            placeholder="https://youtube.com/watch?v=..."
            value={sourceUri}
            onChange={(e) => setSourceUri(e.target.value)}
          />
          <p className="text-xs text-[var(--text-muted)]">
            Paste a link from YouTube, TikTok, Twitter, or any supported platform
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          <Label>File</Label>
          {uploadedFile ? (
            <div className="flex items-center gap-3 rounded-lg border border-[var(--border-subtle)] p-3">
              <FileVideo className="h-5 w-5 text-[var(--text-muted)] shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                  {uploadedFile.name}
                </p>
                <p className="text-xs text-[var(--text-muted)]">
                  {(uploadedFile.size / 1024 / 1024).toFixed(1)} MB
                </p>
              </div>
              <button onClick={clearFile} className="p-1 hover:bg-[var(--bg-subtle)] rounded">
                <X className="h-4 w-4 text-[var(--text-muted)]" />
              </button>
            </div>
          ) : (
            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={cn(
                'flex flex-col items-center gap-2 rounded-lg border-2 border-dashed p-8 cursor-pointer transition-colors',
                isDragging
                  ? 'border-[var(--accent)] bg-[var(--accent-light)]'
                  : 'border-[var(--border-subtle)] hover:border-[var(--border-strong)]',
              )}
            >
              <Upload className="h-8 w-8 text-[var(--text-muted)]" />
              <p className="text-sm text-[var(--text-secondary)]">
                Drop a file here or click to browse
              </p>
              <p className="text-xs text-[var(--text-muted)]">Max 100 MB</p>
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*,audio/*,image/*"
            onChange={handleFileChange}
            className="hidden"
          />
          {uploadProgress !== null && (
            <div className="w-full bg-[var(--bg-subtle)] rounded-full h-2">
              <div
                className="bg-brand h-2 rounded-full transition-all"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          )}
          {uploadError && (
            <p className="text-sm text-red-500">{uploadError}</p>
          )}
        </div>
      )}
    </div>
  )
}
