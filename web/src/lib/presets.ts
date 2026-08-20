export type ParamType =
  | 'timecode'
  | 'enum'
  | 'integer'
  | 'float'
  | 'boolean'
  | 'string'
  | 'url'
  | 'array'
  | 'object'

export interface ParamField {
  type: ParamType
  required: boolean
  default?: unknown
  values?: string[]
  min?: number
  max?: number
  placeholder?: string
  hint?: string
  items?: ParamField
  fields?: Record<string, ParamField>
}

export interface OperationDefinition {
  name: string
  label: string
  description: string
  icon: string
  category: 'transformative' | 'combinatory' | 'conversion'
  inputTypes: string[]
  outputType: string
  params: Record<string, ParamField>
}

export const OPERATIONS: OperationDefinition[] = [
  {
    name: 'download',
    label: 'Download',
    description: 'Save the source file as-is, no processing.',
    icon: 'Download',
    category: 'transformative',
    inputTypes: ['video', 'audio'],
    outputType: 'video',
    params: {},
  },
  {
    name: 'trim',
    label: 'Trim',
    description: 'Cut a clip from a longer video or audio file.',
    icon: 'Scissors',
    category: 'transformative',
    inputTypes: ['video', 'audio'],
    outputType: 'video',
    params: {
      start: { type: 'timecode', required: true, placeholder: '0:00', hint: 'Where to start the clip' },
      end: { type: 'timecode', required: false, placeholder: '1:30', hint: 'Where to stop (leave empty for end)' },
    },
  },
  {
    name: 'cut',
    label: 'Cut',
    description: 'Keep multiple segments from a video, removing the rest.',
    icon: 'Scissors',
    category: 'transformative',
    inputTypes: ['video', 'audio'],
    outputType: 'video',
    params: {
      segments: {
        type: 'array',
        required: true,
        items: {
          type: 'object',
          required: true,
          fields: {
            start: { type: 'timecode', required: true, placeholder: '0:00' },
            end: { type: 'timecode', required: true, placeholder: '0:30' },
          },
        },
      },
    },
  },
  {
    name: 'compress',
    label: 'Compress',
    description: 'Reduce file size while keeping quality.',
    icon: 'Minimize2',
    category: 'transformative',
    inputTypes: ['video', 'audio'],
    outputType: 'video',
    params: {
      quality: { type: 'enum', required: false, default: 'medium', values: ['low', 'medium', 'high'], hint: 'Lower = smaller file, lower quality' },
      resolution: { type: 'enum', required: false, values: ['360p', '480p', '720p', '1080p', '1440p', '4k'], hint: 'Leave empty to keep original' },
    },
  },
  {
    name: 'transcode',
    label: 'Transcode',
    description: 'Convert to a different video format (MP4, WebM, MOV).',
    icon: 'RefreshCw',
    category: 'transformative',
    inputTypes: ['video'],
    outputType: 'video',
    params: {
      format: { type: 'enum', required: true, values: ['mp4', 'webm', 'mov'], hint: 'Target container format' },
      resolution: { type: 'enum', required: false, values: ['360p', '480p', '720p', '1080p', '1440p', '4k'], hint: 'Leave empty to keep original' },
    },
  },
  {
    name: 'resize',
    label: 'Resize',
    description: 'Change dimensions to fit any platform.',
    icon: 'Maximize2',
    category: 'transformative',
    inputTypes: ['video'],
    outputType: 'video',
    params: {
      width: { type: 'integer', required: false, min: 1, max: 7680, hint: 'Pixel width (must be even)' },
      height: { type: 'integer', required: false, min: 1, max: 4320, hint: 'Pixel height (must be even)' },
      preset: { type: 'enum', required: false, values: ['360p', '480p', '720p', '1080p', '1440p', '4k'], hint: 'Quality preset' },
      orientation: { type: 'enum', required: false, values: ['landscape', 'portrait', 'square'], hint: 'Aspect ratio' },
      resolution: { type: 'enum', required: false, values: ['360p', '480p', '720p', '1080p', '1440p', '4k'], hint: 'Resolution target' },
    },
  },
  {
    name: 'watermark',
    label: 'Watermark',
    description: 'Overlay an image on the video.',
    icon: 'Droplets',
    category: 'transformative',
    inputTypes: ['video'],
    outputType: 'video',
    params: {
      image_url: { type: 'url', required: true, placeholder: 'https://example.com/logo.png', hint: 'Publicly accessible image URL' },
      position: { type: 'enum', required: false, default: 'bottom_right', values: ['top_left', 'top_right', 'bottom_left', 'bottom_right', 'center'] },
    },
  },
  {
    name: 'subtitle',
    label: 'Subtitle',
    description: 'Burn subtitles into the video.',
    icon: 'Subtitles',
    category: 'transformative',
    inputTypes: ['video'],
    outputType: 'video',
    params: {
      file_url: { type: 'url', required: false, placeholder: 'https://example.com/subs.srt', hint: 'URL to SRT subtitle file' },
      auto: { type: 'boolean', required: false, default: false, hint: 'Auto-generate (not yet available)' },
    },
  },
  {
    name: 'mute',
    label: 'Mute',
    description: 'Remove the audio track from a video.',
    icon: 'VolumeX',
    category: 'transformative',
    inputTypes: ['video'],
    outputType: 'video',
    params: {},
  },
  {
    name: 'meme',
    label: 'Meme',
    description: 'Add a text caption band to a video or image.',
    icon: 'MessageSquare',
    category: 'transformative',
    inputTypes: ['video', 'audio', 'image'],
    outputType: 'video',
    params: {
      caption: { type: 'string', required: false, placeholder: 'Your caption here', hint: 'Text to overlay' },
      position: { type: 'enum', required: false, default: 'top', values: ['top', 'bottom'] },
    },
  },
  {
    name: 'join',
    label: 'Join',
    description: 'Merge multiple clips into one.',
    icon: 'Link',
    category: 'combinatory',
    inputTypes: ['video', 'audio'],
    outputType: 'video',
    params: {
      clips: {
        type: 'array',
        required: true,
        items: { type: 'url', required: true, placeholder: 'https://example.com/clip.mp4' },
      },
      resolution: { type: 'enum', required: false, values: ['480p', '720p', '1080p', '1440p', '4k'], hint: 'Uniform output resolution' },
    },
  },
  {
    name: 'extract_audio',
    label: 'Extract Audio',
    description: 'Pull the audio track from any video.',
    icon: 'Music',
    category: 'conversion',
    inputTypes: ['video'],
    outputType: 'audio',
    params: {
      format: { type: 'enum', required: false, default: 'mp3', values: ['mp3', 'aac'] },
    },
  },
  {
    name: 'thumbnail',
    label: 'Thumbnail',
    description: 'Grab a single frame as an image.',
    icon: 'Camera',
    category: 'conversion',
    inputTypes: ['video'],
    outputType: 'image',
    params: {
      timestamp: { type: 'timecode', required: true, placeholder: '0:30', hint: 'The frame to capture' },
    },
  },
  {
    name: 'gif',
    label: 'Make GIF',
    description: 'Create an animated GIF from a video clip.',
    icon: 'Image',
    category: 'conversion',
    inputTypes: ['video'],
    outputType: 'gif',
    params: {
      start: { type: 'timecode', required: true, placeholder: '0:00', hint: 'When to start the GIF' },
      end: { type: 'timecode', required: false, placeholder: '0:05', hint: 'When to stop (empty = end of video)' },
      fps: { type: 'integer', required: false, default: 15, min: 1, max: 30, hint: 'Frames per second' },
    },
  },
]

export function getOperation(name: string): OperationDefinition | undefined {
  return OPERATIONS.find((op) => op.name === name)
}

export function getOperationsByCategory(): Record<string, OperationDefinition[]> {
  const grouped: Record<string, OperationDefinition[]> = {}
  for (const op of OPERATIONS) {
    if (!grouped[op.category]) grouped[op.category] = []
    grouped[op.category].push(op)
  }
  return grouped
}

export const CATEGORY_LABELS: Record<string, string> = {
  transformative: 'Transform',
  combinatory: 'Combine',
  conversion: 'Convert',
}

export function getDefaultParams(op: OperationDefinition): Record<string, unknown> {
  const params: Record<string, unknown> = {}
  for (const [key, field] of Object.entries(op.params)) {
    if (field.default !== undefined) {
      params[key] = field.default
    } else if (field.type === 'array') {
      params[key] = []
    } else if (field.type === 'boolean') {
      params[key] = false
    }
  }
  return params
}

export function validateRequiredParams(
  op: OperationDefinition,
  params: Record<string, unknown>,
): string[] {
  const errors: string[] = []
  for (const [key, field] of Object.entries(op.params)) {
    if (!field.required) continue
    const val = params[key]
    if (val === undefined || val === null || val === '') {
      errors.push(`${key} is required`)
    }
    if (field.type === 'array' && Array.isArray(val) && val.length === 0) {
      errors.push(`${key} must have at least one item`)
    }
  }
  return errors
}
