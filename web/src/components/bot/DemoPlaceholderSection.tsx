import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState, useCallback } from 'react'
import { Paperclip, Mic, Video } from 'lucide-react'

// Telegram brand icon — same SVG used in PlatformsSection
function TelegramIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
      <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
    </svg>
  )
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-3 py-2.5">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="h-2 w-2 rounded-full bg-[#ABABAB]"
          animate={{ scale: [1, 1.45, 1], opacity: [0.5, 1, 0.5] }}
          transition={{
            duration: 0.7,
            delay: i * 0.18,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  )
}

function BotAvatar() {
  return (
    <div className="h-6 w-6 rounded-full bg-[#229ED9] flex items-center justify-center shrink-0 self-end">
      <TelegramIcon className="h-3 w-3 text-white" />
    </div>
  )
}

// ── Animation step constants ─────────────────────────────────────
const STEP_HEADER = 1
const STEP_BOT_WELCOME = 2
const STEP_USER_FILE = 3
const STEP_USER_TEXT = 4
const STEP_TYPING = 5
const STEP_BOT_REPLY = 6
const STEP_BOT_FILE = 7
const LOOP_DELAY_MS = 7500

const SLIDE_IN_FROM_LEFT = {
  initial: { x: -18, opacity: 0 },
  animate: { x: 0, opacity: 1 },
  transition: { duration: 0.35, ease: 'easeOut' },
} as const

const SLIDE_IN_FROM_RIGHT = {
  initial: { x: 18, opacity: 0 },
  animate: { x: 0, opacity: 1 },
  transition: { duration: 0.35, ease: 'easeOut' },
} as const

// ── Animated chat demo ───────────────────────────────────────────
function AnimatedChatDemo({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const timers = [
      setTimeout(() => setStep(STEP_HEADER), 400),
      setTimeout(() => setStep(STEP_BOT_WELCOME), 900),
      setTimeout(() => setStep(STEP_USER_FILE), 1900),
      setTimeout(() => setStep(STEP_USER_TEXT), 2900),
      setTimeout(() => setStep(STEP_TYPING), 3900),
      setTimeout(() => setStep(STEP_BOT_REPLY), 5000),
      setTimeout(() => setStep(STEP_BOT_FILE), 5550),
    ]
    const loop = setTimeout(onComplete, LOOP_DELAY_MS)
    return () => {
      timers.forEach(clearTimeout)
      clearTimeout(loop)
    }
  }, [onComplete])

  return (
    <motion.div
      className="mx-auto w-full max-w-[288px]"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="rounded-[2rem] overflow-hidden shadow-2xl border border-[var(--border-subtle)]">

        {/* ── Telegram header ─────────────────────────────────── */}
        <AnimatePresence>
          {step >= STEP_HEADER && (
            <motion.div
              className="flex items-center gap-2.5 px-4 py-3 bg-[#229ED9]"
              initial={{ y: -24, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.35, ease: 'easeOut' }}
            >
              <div className="h-8 w-8 rounded-full bg-white/25 flex items-center justify-center shrink-0">
                <TelegramIcon className="h-4 w-4 text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-white leading-tight">Flume Bot</p>
                <p className="text-[10px] text-white/75 leading-tight">● online</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Chat area ───────────────────────────────────────── */}
        <div className="flex flex-col gap-2 p-3 min-h-[340px] bg-[#EFEBE6] dark:bg-[#1C1C1E]">

          {/* Bot welcome */}
          {step >= STEP_BOT_WELCOME && (
            <motion.div className="flex items-end gap-1.5" {...SLIDE_IN_FROM_LEFT}>
              <BotAvatar />
              <div className="max-w-[82%] rounded-2xl rounded-bl-sm bg-white dark:bg-[#2C2C2E] px-3 py-2 shadow-sm">
                <p className="text-xs text-black dark:text-white leading-relaxed">
                  Hi! Send me a video or paste a link 🎬
                </p>
              </div>
            </motion.div>
          )}

          {/* User — video file bubble */}
          {step >= STEP_USER_FILE && (
            <motion.div className="flex justify-end" {...SLIDE_IN_FROM_RIGHT}>
              <div className="max-w-[82%] rounded-2xl rounded-br-sm bg-[#EFFDDE] dark:bg-[#2B5278] px-3 py-2.5 shadow-sm">
                <div className="flex items-center gap-2">
                  <div className="h-7 w-7 rounded-lg bg-black/10 dark:bg-white/10 flex items-center justify-center shrink-0">
                    <Video className="h-3.5 w-3.5 text-black/60 dark:text-white/60" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-black dark:text-white truncate">video.mp4</p>
                    <p className="text-[10px] text-black/50 dark:text-white/50">14.2 MB</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* User — text instruction */}
          {step >= STEP_USER_TEXT && (
            <motion.div className="flex justify-end" {...SLIDE_IN_FROM_RIGHT}>
              <div className="max-w-[82%] rounded-2xl rounded-br-sm bg-[#EFFDDE] dark:bg-[#2B5278] px-3 py-2 shadow-sm">
                <p className="text-xs text-black dark:text-white leading-relaxed">
                  Trim to the first 30 seconds
                </p>
              </div>
            </motion.div>
          )}

          {/* Bot — typing indicator / reply (mutually exclusive via AnimatePresence) */}
          <div className="flex items-end gap-1.5">
            {(step === STEP_TYPING || step >= STEP_BOT_REPLY) && <BotAvatar />}

            <AnimatePresence mode="wait">
              {step === STEP_TYPING && (
                <motion.div
                  key="typing"
                  className="rounded-2xl rounded-bl-sm bg-white dark:bg-[#2C2C2E] shadow-sm"
                  initial={{ opacity: 0, scale: 0.88 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.88 }}
                  transition={{ duration: 0.22 }}
                >
                  <TypingIndicator />
                </motion.div>
              )}

              {step >= STEP_BOT_REPLY && (
                <motion.div
                  key="reply"
                  className="max-w-[82%] rounded-2xl rounded-bl-sm bg-white dark:bg-[#2C2C2E] px-3 py-2 shadow-sm"
                  {...SLIDE_IN_FROM_LEFT}
                >
                  <p className="text-xs text-black dark:text-white leading-relaxed mb-1.5">
                    ✅ Done! Here's your clip:
                  </p>

                  {/* Bot — file attachment bubble */}
                  {step >= STEP_BOT_FILE && (
                    <motion.div
                      className="flex items-center gap-2 bg-black/5 dark:bg-white/5 rounded-lg px-2.5 py-1.5"
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, ease: 'easeOut' }}
                    >
                      <Paperclip className="h-3.5 w-3.5 text-[#229ED9] shrink-0" />
                      <span className="text-[10px] font-medium text-black dark:text-white truncate">
                        video_trimmed.mp4
                      </span>
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* ── Telegram input bar ──────────────────────────────── */}
        <div className="flex items-center gap-2.5 px-3 py-2.5 bg-[#F0F0F0] dark:bg-[#2C2C2E] border-t border-black/5 dark:border-white/5">
          <Paperclip className="h-5 w-5 text-[#ABABAB] shrink-0" />
          <div className="flex-1 rounded-full bg-white dark:bg-[#3A3A3C] px-3.5 py-1.5">
            <p className="text-xs text-[#ABABAB]">Message Flume Bot…</p>
          </div>
          <Mic className="h-5 w-5 text-[#ABABAB] shrink-0" />
        </div>

      </div>
    </motion.div>
  )
}

// ── Section ──────────────────────────────────────────────────────
export function DemoPlaceholderSection() {
  const [loopKey, setLoopKey] = useState(0)

  const handleComplete = useCallback(() => {
    setLoopKey((k) => k + 1)
  }, [])

  return (
    <section className="py-20 sm:py-24 bg-[var(--bg-subtle)]">
      {/* PLACEHOLDER: animated chat demo */}
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        <div className="text-center mb-14">
          <p className="text-label text-brand mb-3">See it in action</p>
          <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
            As easy as sending a message
          </h2>
        </div>

        <AnimatedChatDemo key={loopKey} onComplete={handleComplete} />

      </div>
    </section>
  )
}
