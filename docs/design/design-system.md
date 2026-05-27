# Flume Design System

> **Purpose:** This document is the single source of truth for Flume's frontend visual language. Any AI agent or engineer extending the UI must read this first and follow every convention here to avoid breaking the design.

---

## 1 — Design Language

Flume presents as a clean, minimal, developer-facing SaaS product. The visual language is intentionally restrained — generous whitespace, a single green brand accent, and expressive typography used sparingly as a contrast against workhorse UI text.

| Principle | Expression |
|---|---|
| Minimal | No decorative elements. Every visual element earns its space. |
| Developer-native | Monospace labels, tight grids, code-like precision in spacing |
| Expressive headings | Instrument Serif italic headings contrast with DM Sans body — this pairing is non-negotiable |
| One accent | Brand green (`#1D9E75`) is the only color accent. Never introduce a second accent color. |
| Dark mode first | All tokens are defined for both light and dark. Never hardcode a light-only color. |

---

## 2 — Design Tokens

**Source of truth:** `web/src/lib/tokens.css`  
**Tailwind exposure:** `web/src/index.css` → `@theme inline` block

All CSS variables must be defined in `tokens.css` for both `:root` (light) and `.dark`. After adding a variable, expose it in the `@theme inline` block in `index.css` if a Tailwind utility is needed.

### 2.1 Brand Colors

| Token | CSS Variable | Tailwind Utility | Value (light + dark) | Usage |
|---|---|---|---|---|
| Brand | `--brand` | `text-brand` `bg-brand` | `#1D9E75` | CTAs, eyebrow labels, icon tints, active states |
| Brand Mid | `--brand-mid` | `text-brand-mid` | `#9FE1CB` | Step connectors, focus rings, dashed borders |
| Brand Hover | `--brand-hover` | `text-brand-hover` | `#085041` | Button hover/pressed background |
| Brand Light | `--brand-light` | `bg-[var(--brand-light)]` | `rgba(29,158,117,0.10)` | Icon container fills, card accent backgrounds, gradient base |

### 2.2 Surface Colors

| Token | CSS Variable | Tailwind Utility | Light | Dark | Usage |
|---|---|---|---|---|---|
| Page background | `--background` | `bg-background` | `#F8F9FA` | `#0C0C0E` | Base page background |
| Card | `--card` | `bg-card` / `bg-[var(--bg-card)]` | `#FFFFFF` | `#131318` | Card / surface backgrounds |
| Subtle | `--bg-subtle` | `bg-[var(--bg-subtle)]` | `#F1F3F4` | `#1A1A22` | Alternate section backgrounds, input fills |

### 2.3 Text Colors

| Token | CSS Variable | Tailwind Utility | Light | Dark | Usage |
|---|---|---|---|---|---|
| Primary text | `--foreground` | `text-foreground` `text-[var(--text-primary)]` | `#1A1A22` | `#F0F0F4` | All headings and primary body text |
| Secondary text | `--muted-foreground` | `text-muted-foreground` `text-[var(--text-secondary)]` | `#5A5A72` | `#9090A8` | Descriptions, card body, nav links |
| Muted text | `--text-muted` | `text-[var(--text-muted)]` | `#9090A8` | `#5A5A72` | Timestamps, footer fine print, placeholders |

### 2.4 Border Colors

| Token | CSS Variable | Light | Dark | Usage |
|---|---|---|---|---|
| Subtle border | `--border` | `rgba(0,0,0,0.07)` | `rgba(255,255,255,0.07)` | Default card / section borders |
| Strong border | `--border-strong` | `rgba(0,0,0,0.14)` | `rgba(255,255,255,0.14)` | Hover state border on cards |

Use: `border-border` or `border-[var(--border-subtle)]` for default, `border-[var(--border-strong)]` on hover.

### 2.5 shadcn Semantic Tokens

These are required by shadcn components. Never rename or remove them. Both `:root` and `.dark` values are defined in `tokens.css`.

```
--primary / --primary-foreground       → brand green / white
--secondary / --secondary-foreground   → subtle fill / dark text
--muted / --muted-foreground           → subtle fill / secondary text
--accent / --accent-foreground         → brand light fill / dark text
--destructive / --destructive-foreground → #EF4444 / white
--popover / --popover-foreground
--card / --card-foreground
--input                                → form input background
--ring                                 → #9FE1CB (focus ring)
--radius                               → 8px (base, scaled by multipliers)
```

### 2.6 Border Radius Scale

```css
--radius-sm:  calc(var(--radius) * 0.6)   /* ~5px  */
--radius-md:  calc(var(--radius) * 0.8)   /* ~6px  */
--radius-lg:  var(--radius)               /* 8px   */
--radius-xl:  calc(var(--radius) * 1.4)   /* ~11px */
--radius-2xl: calc(var(--radius) * 1.8)   /* ~14px */
--radius-3xl: calc(var(--radius) * 2.2)   /* ~18px */
--radius-4xl: calc(var(--radius) * 2.6)   /* ~21px */
```

In Tailwind: `rounded-xl` = `--radius-xl`. For cards use `rounded-xl`. For icon containers use `rounded-lg` (compact) or `rounded-xl` (large surface cards).

---

## 3 — Typography

**Font stack:**
- **UI / body:** `DM Sans` — loaded via `@fontsource/dm-sans` (weights 400, 500, 600, 700)
- **Display / headings:** `Instrument Serif` italic — loaded via `@fontsource/instrument-serif` (400-italic only)

These are set in `@theme inline` as `--font-sans` and `--font-serif`.

### 3.1 Utility Classes

| Class | CSS Definition | Usage |
|---|---|---|
| `.text-display` | `font-family: Instrument Serif; font-style: italic; font-weight: 400; line-height: 1.05; letter-spacing: -0.02em` | **All** section headings and hero H1s |
| `.text-label` | `font-size: 11px; font-weight: 500; letter-spacing: 0.07em; text-transform: uppercase` | Section eyebrow labels |

Both are defined as plain classes (not `@utility`) in `index.css`. Do not add pseudo-selectors or variants to them.

### 3.2 Type Scale

```
Hero H1:        .text-display  text-4xl sm:text-5xl lg:text-[3.75rem]  text-[var(--text-primary)]
Section H2:     .text-display  text-3xl sm:text-4xl                   text-[var(--text-primary)]
Card H3:        font-semibold  text-base                               text-[var(--text-primary)]
Surface card H3: font-semibold text-xl                                 text-[var(--text-primary)]
Body large:     text-lg        leading-relaxed                         text-[var(--text-secondary)]
Body:           text-sm        leading-relaxed                         text-[var(--text-secondary)]
Caption:        text-xs                                                text-[var(--text-muted)]
Eyebrow:        .text-label    text-brand  mb-3
```

### 3.3 Rules

- `.text-display` is **exclusive to headings**. Never apply it to body text, captions, or labels.
- `.text-label` is **exclusive to eyebrow labels** above headings. Do not use it for badges, tags, or navigation items.
- Do not introduce new font families. DM Sans and Instrument Serif are the complete font set.

---

## 4 — Layout & Spacing

### 4.1 The Standard Container

**Every section uses exactly this container. No exceptions. No `max-w-4xl`, no `max-w-5xl` on sections.**

```jsx
<div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
```

For centered prose blocks within a section (hero text, CTA copy):
```jsx
<div className="mx-auto max-w-3xl text-center">   {/* hero, large CTA */}
<div className="mx-auto max-w-2xl text-center">   {/* small CTA, confirmation blocks */}
```

The pricing grid uses `max-w-5xl mx-auto` as an inner constraint within the standard container.

### 4.2 Section Vertical Rhythm

```
py-20 sm:py-24            →  all standard content sections
py-20 sm:py-28 lg:py-32   →  hero sections only (BotHeroSection, HeroSection)
mb-14                     →  spacing below the section header block (eyebrow + heading)
```

### 4.3 Grid Columns

| Content | Grid |
|---|---|
| Feature cards (4 items) | `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5` |
| Capability cards (6 items) | `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5` |
| Two surfaces / Platforms | `grid-cols-1 md:grid-cols-2 gap-5` |
| Pricing tiers | `grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl mx-auto` |
| Footer | `grid-cols-2 sm:grid-cols-4 gap-8` |

### 4.4 Section Background Alternation

Sections alternate between the two surface backgrounds. The pattern for each page:

**Landing:** Hero (default) → Features (subtle) → HowItWorks (default) → Pricing (default) → TwoSurfaces (subtle) → CTA (default + gradient)

**Bot:** BotHero (default) → Demo (subtle) → HowItWorks (default) → Capabilities (subtle) → Platforms (default) → CTA (default + gradient)

```jsx
// Default
<section className="py-20 sm:py-24">

// Alternate
<section className="py-20 sm:py-24 bg-[var(--bg-subtle)]">
```

---

## 5 — Section Anatomy

Every section on every page follows this exact structure. This is non-negotiable.

```jsx
<section id="section-id" className="py-20 sm:py-24 [optional: bg-[var(--bg-subtle)]]">
  <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

    {/* ── Section header ─────────────────────────────────────── */}
    <div className="text-center mb-14">
      <p className="text-label text-brand mb-3">Eyebrow label</p>
      <h2 className="text-display text-3xl sm:text-4xl text-[var(--text-primary)]">
        Section headline goes here
      </h2>
      {/* Optional subtext — only when the heading needs elaboration */}
      <p className="mt-4 text-lg text-[var(--text-secondary)]">
        Supporting sentence.
      </p>
    </div>
    {/* ────────────────────────────────────────────────────────── */}

    {/* Section content: grid, steps, cards, etc. */}

  </div>
</section>
```

**Rules:**
- Never omit the eyebrow label. Every section has one.
- Never use `text-display` for the eyebrow — only `.text-label`.
- `mb-14` on the header block is fixed. Do not change it to `mb-12` or `mb-16`.

---

## 6 — Components

### 6.1 Button

**Rule:** All interactive or navigational elements that visually look like buttons must use `buttonVariants` from `@/components/ui/button`. Never style a raw `<a>` or `<button>` manually.

```tsx
import { buttonVariants } from '@/components/ui/button'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

// ── Link styled as a button (navigation, external links, anchors) ──
<a
  href="..."
  className={cn(buttonVariants({ variant: 'default', size: 'lg' }), 'px-6 gap-2')}
>
  Label <ArrowRight className="h-4 w-4" />
</a>

// ── Interactive button (event handlers, toggles) ──
<Button variant="ghost" size="icon" onClick={...} aria-label="Describe action">
  <Icon className="h-4 w-4" />
</Button>
```

#### Variant usage

| Variant | When to use |
|---|---|
| `default` | Primary CTA — filled brand green. Use once per section at most. |
| `outline` | Secondary CTA — paired with a `default` button. |
| `ghost` | Icon-only utility buttons (theme toggle, mobile menu trigger). |
| `secondary` | Lower-priority actions with no strong visual weight. |

#### Size usage

| Size | When to use |
|---|---|
| `lg` | Hero and CTA section CTAs |
| `default` | Section-level CTAs, mobile sticky bar buttons |
| `sm` | Card-level CTAs (`self-start`) |
| `icon` | Square icon-only buttons (`h-10 w-10`) |

#### CTA pairing pattern

Every CTA block has a **primary** + **secondary** pair:
```jsx
<div className="flex flex-col sm:flex-row items-center justify-center gap-3">
  <a href="..." className={cn(buttonVariants({ variant: 'default', size: 'lg' }), 'px-6 gap-2')}>
    Primary Action <Icon className="h-4 w-4" />
  </a>
  <a href="..." className={cn(buttonVariants({ variant: 'outline', size: 'lg' }), 'px-6 gap-2')}>
    <Icon className="h-4 w-4" /> Secondary Action
  </a>
</div>
```

### 6.2 Card

Standard card pattern used across feature grids, capability grids, and surface cards:

```jsx
// Compact card (features, capabilities — p-6)
<div className="group rounded-xl bg-[var(--bg-card)] p-6 border border-[var(--border-subtle)] hover:border-[var(--border-strong)] hover:shadow-sm transition-all duration-200">
  {/* Icon container */}
  <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--brand-light)]">
    <Icon className="h-5 w-5 text-brand" />
  </div>
  <h3 className="font-semibold text-[var(--text-primary)] mb-2">Title</h3>
  <p className="text-sm text-[var(--text-secondary)] leading-relaxed">Description</p>
</div>

// Large surface card (TwoSurfaces, Platforms — p-8)
<div className="group rounded-xl bg-[var(--bg-card)] p-8 border border-[var(--border-subtle)] hover:border-[var(--border-strong)] hover:shadow-sm transition-all duration-200 flex flex-col">
  {/* Icon container */}
  <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--brand-light)]">
    <Icon className="h-6 w-6 text-brand" />
  </div>
  <h3 className="text-xl font-semibold text-[var(--text-primary)]">Title</h3>
  <p className="text-sm text-[var(--text-secondary)] leading-relaxed flex-1 mb-6">Description</p>
  {/* Card CTA */}
  <a href="..." className={cn(buttonVariants({ variant: 'default', size: 'sm' }), 'self-start gap-1.5 px-4')}>
    CTA <ArrowRight className="h-3.5 w-3.5" />
  </a>
</div>
```

**Rules:**
- `hover:shadow-sm` + `hover:border-[var(--border-strong)]` on every interactive card. Never omit.
- `transition-all duration-200` on every card.
- Icon container color is always `bg-[var(--brand-light)]`, icon is always `text-brand`.

### 6.3 Step Connectors (HowItWorks)

Used in both the landing and bot `HowItWorks` sections. The step circle and dashed connector between steps are a visual signature.

```tsx
import React from 'react'

<div className="flex flex-col md:flex-row items-start gap-8 md:gap-0">
  {steps.map((step, index) => (
    <React.Fragment key={step.number}>
      {/* Step */}
      <div className="flex-1 flex flex-col items-center text-center px-4 md:px-6">
        <div className="h-12 w-12 rounded-full bg-[var(--brand-light)] border-2 border-[var(--brand-mid)] flex items-center justify-center mb-5 shrink-0">
          <span className="text-sm font-bold text-brand">{step.number}</span>
        </div>
        <h3 className="text-base font-semibold text-[var(--text-primary)] mb-2">{step.title}</h3>
        <p className="text-sm text-[var(--text-secondary)] leading-relaxed max-w-[220px]">{step.description}</p>
      </div>

      {/* Dashed connector — desktop only, between steps */}
      {index < steps.length - 1 && (
        <div className="hidden md:block shrink-0 w-12 lg:w-16 pt-6">
          <div className="border-t-2 border-dashed border-[var(--brand-mid)] w-full" />
        </div>
      )}
    </React.Fragment>
  ))}
</div>
```

Step numbers are zero-padded strings: `'01'`, `'02'`, `'03'`.

### 6.4 Pricing Tier Card

The highlighted (recommended) tier uses a visual ring and scale treatment. Only one tier can be `highlighted: true`.

```tsx
<div className={cn(
  'relative rounded-xl bg-[var(--bg-card)] p-8 flex flex-col border transition-all duration-200',
  tier.highlighted
    ? 'border-[var(--brand)] ring-1 ring-[var(--brand)] shadow-lg scale-[1.02]'
    : 'border-[var(--border-subtle)] hover:border-[var(--border-strong)] hover:shadow-sm'
)}>
  {/* Recommended badge — positioned above the card */}
  {tier.highlighted && (
    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
      <Badge variant="default" className="px-3 py-0.5 text-xs font-semibold">
        Recommended
      </Badge>
    </div>
  )}
  {/* ... pricing card content ... */}
</div>
```

Feature list items always use a `Check` icon:
```tsx
<li className="flex items-start gap-2.5">
  <Check className="h-4 w-4 text-brand mt-0.5 shrink-0" />
  <span className="text-sm text-[var(--text-secondary)]">{feature}</span>
</li>
```

### 6.5 Badge

From `@/components/ui/badge`.

| Variant | Usage |
|---|---|
| `default` | "Recommended" on the highlighted pricing tier |
| `secondary` | "Coming soon" state labels (e.g. WhatsApp platform) |

### 6.6 Navbar

```
Sticky: sticky top-0 z-50
Height: h-16
Background: bg-[var(--bg)]/80 backdrop-blur-md
Border: border-b border-[var(--border-subtle)]
Container: mx-auto max-w-7xl (wider than sections — intentional)
```

Mobile sheet: uses shadcn `Sheet` (backed by `@base-ui/react/dialog`). The `SheetTrigger` uses the `render` prop pattern — **not `asChild`**:

```tsx
<SheetTrigger
  render={
    <Button
      variant="ghost"
      size="icon"
      className="md:hidden"
      aria-label="Open navigation menu"
    />
  }
>
  <Menu className="h-5 w-5" />
</SheetTrigger>
```

All nav links inside the mobile sheet must call `setMobileOpen(false)` in their `onClick` handler.

Internal routes use React Router `<Link to="...">`. Anchor/external links use `<a href="...">`.

### 6.7 Section Gradient Backgrounds

Two gradient utilities are available for Hero and CTA sections:

```jsx
// Hero — radial glow from top center
<section className="relative overflow-hidden ...">
  <div className="gradient-hero absolute inset-0 -z-10" />
  ...
</section>

// CTA — radial glow from bottom center
<section className="relative ...">
  <div className="gradient-cta absolute inset-0 -z-10" />
  ...
</section>
```

These are defined in `@layer components` in `index.css`. Do not replicate them as inline `style={{}}` props.

### 6.8 Animated Chat Demo (DemoPlaceholderSection)

**File:** `web/src/components/bot/DemoPlaceholderSection.tsx`  
**Dependency:** `framer-motion` (added to `web/package.json`)

The demo simulates the **real Telegram interface** users see when interacting with Flume Bot. It is not a Flume-branded chat — it deliberately uses Telegram's own visual language to make the product story concrete.

#### Component structure

```
DemoPlaceholderSection          ← section wrapper; holds loopKey state
└── AnimatedChatDemo key={loopKey}  ← remounts on each loop to reset all animation state
      ├── TelegramIcon            ← inline SVG (same as PlatformsSection)
      ├── Telegram header         ← bg #229ED9, slides down on mount
      ├── Chat area               ← 6 sequenced motion.div elements
      │     ├── BotAvatar         ← small #229ED9 circle with TelegramIcon
      │     ├── Bot welcome bubble
      │     ├── User file bubble  (video.mp4)
      │     ├── User text bubble  ("Trim to the first 30 seconds")
      │     ├── TypingIndicator   ← 3 pulsing dots, AnimatePresence exit
      │     ├── Bot reply bubble  ("✅ Done! Here's your clip:")
      │     └── Bot file attachment (video_trimmed.mp4)
      └── Telegram input bar      ← static chrome
```

#### Loop mechanism

`DemoPlaceholderSection` increments a `loopKey` state via a `useCallback` passed as `onComplete`. `AnimatedChatDemo` receives this as `key={loopKey}`, which causes React to fully unmount and remount the component — cleanly resetting all `useState` and `useEffect` timers on each cycle. The loop fires at **7500 ms**.

#### Animation sequence

| ms | Step | Technique |
|---|---|---|
| 0 | Frame fades + scales in | `opacity: 0→1, scale: 0.95→1` |
| 400 | Header slides down | `y: -24→0, opacity: 0→1` |
| 900 | Bot welcome bubble | slide in from left |
| 1900 | User video file bubble | slide in from right |
| 2900 | User text bubble | slide in from right |
| 3900 | Typing indicator (`● ● ●`) | 3 dots, staggered scale+opacity loop |
| 5000 | Typing exits → bot reply slides in | `AnimatePresence mode="wait"` |
| 5550 | Bot file attachment | `opacity: 0→1, y: 4→0` |
| 7500 | Loop resets | `loopKey` increments, component remounts |

#### Telegram color palette

These colors are **component-scoped** inline values. They must **not** be added to `tokens.css` — they represent Telegram's brand, not Flume's design system.

| Element | Light | Dark (`dark:`) |
|---|---|---|
| Header bg | `#229ED9` | `#229ED9` (unchanged) |
| Chat bg | `#EFEBE6` | `#1C1C1E` |
| Bot bubble bg | `#FFFFFF` | `#2C2C2E` |
| User bubble bg | `#EFFDDE` | `#2B5278` |
| Input bar bg | `#F0F0F0` | `#2C2C2E` |
| Input field bg | `#FFFFFF` | `#3A3A3C` |
| Icon / dot color | `#ABABAB` | `#ABABAB` |

Dark mode is applied via Tailwind `dark:` variants (e.g. `dark:bg-[#1C1C1E]`), which works because of the `@custom-variant dark (&:is(.dark *))` defined in `index.css`.

#### Rules

- Never change the Telegram header color away from `#229ED9` — it is a brand color, not a design token.
- Do not introduce a Flume-branded chat simulation in place of the Telegram one. The product runs on Telegram; the demo should show that.
- The `{/* PLACEHOLDER: animated chat demo */}` comment is retained in the section wrapper as a landmark for future changes.
- To update the animation content (new steps, different copy), edit the `AnimatedChatDemo` internal component and adjust the `setTimeout` cascade in its `useEffect`. Match the `LOOP_DELAY_MS` constant to the last step time + hold duration.

---

## 7 — CSS Utilities

Defined in `web/src/index.css`. Follow Tailwind v4 rules — custom utilities go in `@layer components` or `@utility`.

| Class | Layer | Definition | Usage |
|---|---|---|---|
| `.gradient-hero` | `@layer components` | `radial-gradient(circle at 50% 0%, var(--brand-light) 0%, transparent 60%)` | Hero sections |
| `.gradient-cta` | `@layer components` | `radial-gradient(circle at 50% 100%, var(--brand-light) 0%, transparent 60%)` | CTA sections |
| `.text-display` | (plain class) | Instrument Serif, italic, 400, lh 1.05, ls -0.02em | All headings |
| `.text-label` | (plain class) | 11px, 500, ls 0.07em, uppercase | Eyebrow labels |

### Tailwind v4 rules to follow

- Do **not** use `@apply` with arbitrary CSS classes. Only use it with Tailwind utilities.
- Custom reusable CSS classes go in `@layer components`.
- Custom single-property utilities go in `@utility`.
- CSS variables in utility values use parenthesis syntax: `bg-(--brand-color)`, not `bg-[--brand-color]`.
- In v4, unlayered CSS overrides layered Tailwind utilities. Always wrap global resets in `@layer base`.

---

## 8 — Icons

**Library:** `lucide-react` (pinned at `^0.577` — pre-v1, retains brand/logo icons)

### Sizing convention

| Context | Size |
|---|---|
| Inside buttons | `h-4 w-4` |
| Compact icon container (`h-10 w-10`) | `h-5 w-5` |
| Large icon container (`h-12 w-12`) | `h-6 w-6` |
| Mobile menu icon | `h-5 w-5` |
| Card CTA arrow | `h-3.5 w-3.5` |

### Color convention

- Brand icons: `text-brand`
- Neutral icons: `text-[var(--text-secondary)]`
- White icons (inside colored containers): `text-white`
- Always set color explicitly — never rely on `currentColor` inheritance without intention.

### Platform brand icons (Telegram, WhatsApp)

Telegram and WhatsApp use **inline SVG components** defined locally in each bot component file. Do not use Lucide's generic `MessageCircle` for these platforms. The SVG paths are:

```tsx
// Telegram — #229ED9 brand color
function TelegramIcon({ className }: { className?: string }) {
  return <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
    <path d="M11.944 0A12 12 0 ..." />
  </svg>
}

// WhatsApp — #25D366 brand color
function WhatsAppIcon({ className }: { className?: string }) {
  return <svg viewBox="0 0 24 24" fill="currentColor" className={className} aria-hidden="true">
    <path d="M17.472 14.382c..." />
  </svg>
}
```

These are defined in: `BotHeroSection.tsx`, `PlatformsSection.tsx`, `CTASection.tsx` (bot).

**Platform accent colors (do not change):**
- Telegram: `#229ED9` (icon color, top accent bar, icon container: `bg-[#229ED9]/10`)
- WhatsApp: `#25D366` (icon color, top accent bar, icon container: `bg-[#25D366]/10`)

---

## 9 — Dark Mode

**Mechanism:** `.dark` class on `<html>`. Toggled by the `useTheme` hook (theme toggle button in Navbar).

**Custom variant:** `@custom-variant dark (&:is(.dark *))` defined in `index.css`. This means dark mode styles are applied when any ancestor has the `.dark` class.

**Rules:**
- Every CSS variable in `tokens.css` under `:root` must have a counterpart in `.dark`.
- Never use hardcoded hex colors in component files. Always use a CSS variable that has a dark mode value.
- Tailwind `dark:` prefix works with this setup. Use it for one-off dark overrides when a CSS variable isn't warranted.
- The `Wordmark` component is a pure inline SVG (no PNG assets). It accepts a `variant` prop (`'light' | 'dark' | 'auto'`). Default is `'auto'`, which reads `resolvedTheme` internally — no prop required in most contexts. Pass `variant={resolvedTheme}` explicitly only when the parent already has `resolvedTheme` in scope and wants to force a specific palette (e.g. Navbar).

---

## 10 — Accessibility

| Rule | Implementation |
|---|---|
| All icon-only buttons must have `aria-label` | `<Button ... aria-label="Switch to dark mode">` |
| No nested `<button>` elements | Use `render` prop on base-ui primitives (e.g. `SheetTrigger`) instead of wrapping a `Button` |
| Mobile nav closes on link click | All mobile Sheet nav links call `setMobileOpen(false)` in `onClick` |
| Disabled platform links | Use `aria-disabled="true"` + `tabIndex={-1}` + `pointer-events-none` (not the HTML `disabled` attr on `<a>`) |
| Focus rings | Configured globally via `outline-ring/50` in `@layer base` — do not override this |

---

## 11 — File Structure

```
web/src/
├── components/
│   ├── common/
│   │   ├── Navbar.tsx            ← shared header (sticky, mobile sheet, theme toggle)
│   │   ├── Footer.tsx            ← shared footer (4-column grid)
│   │   └── Wordmark.tsx          ← SVG logo, accepts variant="light"|"dark"
│   │
│   ├── landing/                  ← Landing page sections (in render order)
│   │   ├── HeroSection.tsx
│   │   ├── FeaturesSection.tsx
│   │   ├── HowItWorksSection.tsx
│   │   ├── PricingSection.tsx
│   │   ├── TwoSurfacesSection.tsx
│   │   └── CTASection.tsx
│   │
│   └── bot/                      ← Bot page sections (in render order)
│       ├── BotHeroSection.tsx
│       ├── DemoPlaceholderSection.tsx  ← Telegram-simulated animated chat demo (Framer Motion)
│       ├── HowItWorksSection.tsx
│       ├── CapabilitiesSection.tsx
│       ├── PlatformsSection.tsx
│       └── CTASection.tsx            ← includes sticky mobile CTA bar
│
├── lib/
│   ├── tokens.css    ← ALL CSS variables. Source of truth.
│   └── utils.ts      ← cn() helper (clsx + tailwind-merge)
│
├── pages/
│   ├── LandingPage.tsx   ← composes landing sections + Navbar + Footer
│   └── BotPage.tsx       ← composes bot sections + Navbar + Footer (pb-20 md:pb-0 for sticky bar)
│
├── hooks/
│   └── useTheme.ts   ← returns { resolvedTheme, toggleTheme }
│
└── index.css         ← @import chain, @theme inline, @layer base/components, utilities
```

---

## 12 — Placeholders & Future Work

| File | Status | Note |
|---|---|---|
| `DemoPlaceholderSection.tsx` | ✅ Done | Telegram-simulated animated chat demo. See §6.8 for full documentation. |
| `PricingSection.tsx` | ⚠️ Placeholder data | Pricing tiers and limits are not final. See `// [PLACEHOLDER]` comment in the file. |
| `Footer.tsx` (WhatsApp link) | ⚠️ Dummy link | `https://wa.me/000000000` is a placeholder. Replace with real number before launch. |
| `BotHeroSection.tsx` (WhatsApp) | ⚠️ Dummy link | Same. |
| `PlatformsSection.tsx` (WhatsApp) | ⚠️ Coming soon | WhatsApp card is deliberately disabled (`opacity-75`, `pointer-events-none`). Enable when ready. |

---

## 13 — Adding a New Section (Checklist)

When adding any new section to any page, verify every item:

- [ ] Section uses `py-20 sm:py-24` vertical padding (or `py-20 sm:py-28 lg:py-32` for hero)
- [ ] Container is exactly `mx-auto max-w-6xl px-4 sm:px-6 lg:px-8`
- [ ] Section has a `.text-label text-brand mb-3` eyebrow label
- [ ] Section heading uses `.text-display text-3xl sm:text-4xl text-[var(--text-primary)]`
- [ ] Section header block has `text-center mb-14`
- [ ] Background alternates correctly with adjacent sections (`bg-[var(--bg-subtle)]` or default)
- [ ] All CTAs use `buttonVariants` — no raw styled `<a>` tags
- [ ] All cards have `hover:border-[var(--border-strong)] hover:shadow-sm transition-all duration-200`
- [ ] All icon containers use `bg-[var(--brand-light)]` fill and `text-brand` icon color
- [ ] Any new CSS variable is added to both `:root` and `.dark` in `tokens.css`
- [ ] Any new Tailwind utility is added to `@theme inline` in `index.css`
- [ ] No hardcoded hex color values in the component file
- [ ] Component has no `aria` accessibility regressions (labels on icon buttons, no nested `<button>`)
