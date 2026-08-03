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
| Brand Light | `--brand-light` | `bg-(--brand-light)` | `rgba(29, 158, 117, 0.10)` | Icon container fills, card accent backgrounds, gradient base |

### 2.2 Surface Colors

| Token | CSS Variable | Tailwind Utility | Light | Dark | Usage |
|---|---|---|---|---|---|
| Page background | `--background` | `bg-background` | `#F8F9FA` | `#0C0C0E` | Base page background |
| Card | `--card` | `bg-card` / `bg-(--bg-card)` | `#FFFFFF` | `#131318` | Card / surface backgrounds |
| Subtle | `--bg-subtle` | `bg-(--bg-subtle)` | `#F1F3F4` | `#1A1A22` | Alternate section backgrounds, input fills |

### 2.3 Text Colors

| Token | CSS Variable | Tailwind Utility | Light | Dark | Usage |
|---|---|---|---|---|---|
| Primary text | `--foreground` | `text-foreground` / `text-(--text-primary)` | `#1A1A22` | `#F0F0F4` | All headings and primary body text |
| Secondary text | `--muted-foreground` | `text-muted-foreground` / `text-(--text-secondary)` | `#5A5A72` | `#9090A8` | Descriptions, card body, nav links |
| Muted text | `--text-muted` | `text-(--text-muted)` | `#9090A8` | `#5A5A72` | Timestamps, footer fine print, placeholders |

### 2.4 Border Colors

| Token | CSS Variable | Light | Dark | Usage |
|---|---|---|---|---|
| Subtle border | `--border` | `rgba(0,0,0,0.07)` | `rgba(255,255,255,0.07)` | Default card / section borders |
| Strong border | `--border-strong` | `rgba(0,0,0,0.14)` | `rgba(255,255,255,0.14)` | Hover state border on cards |

Use: `border-border` or `border-(--border-subtle)` for default, `border-(--border-strong)` on hover. Use `border-brand/20` only for brand feedback and `border-destructive/20` only for destructive feedback.

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

**Every public marketing section uses exactly this container.** Dashboard and admin surfaces use the shell containers documented in §15; detail pages may use a narrower reading column inside that shell.

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

## 5 — Marketing Section Anatomy

Every public marketing section follows this exact structure. Dashboard and admin pages use the application-page anatomy in §16 instead.

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
- Marketing sections use an eyebrow label unless the section is an explicitly documented hero or utility section.
- Never use `text-display` for the eyebrow — only `.text-label`.
- `mb-14` on the standard marketing header block is fixed. Do not change it to `mb-12` or `mb-16` without documenting the exception.
- Dashboard page headers do not need an eyebrow when the page title already provides sufficient context. Never add a redundant kicker to an empty state.

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

### 6.9 Wordmark

**File:** `web/src/components/common/Wordmark.tsx`

The Wordmark is the primary Flume brand identity element — an inline SVG combining a three-stripe mark with the logotype "flume" in Instrument Serif italic.

#### Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `variant` | `'light' \| 'dark' \| 'auto'` | `'auto'` | Color palette to render. `'auto'` reads `resolvedTheme` from `useTheme` internally. |
| `className` | `string` | — | Additional Tailwind classes. Default size is `h-8 w-auto`. |

#### Color logic

| Variant | Text color (`currentColor`) |
|---|---|
| `'dark'` | `var(--brand-mid)` — lighter green, readable on dark surfaces |
| `'light'` | `var(--brand-hover)` — deep green, readable on light surfaces |
| `'auto'` | Resolves to the above based on `resolvedTheme` |

#### Mark anatomy

Three diagonal parallelogram stripes stacked vertically (viewBox `0 0 124 32`):

| Stripe | Fill | Visual role |
|---|---|---|
| Top | `var(--brand-light)` | Lightest — creates depth gradient |
| Middle | `var(--brand-mid)` | Mid tone |
| Bottom | `var(--brand)` | Darkest — anchors the mark |

The logotype `"flume"` is rendered as an SVG `<text>` element: Instrument Serif, italic, weight 400, `fontSize=22`, `letterSpacing=-0.44`, `fill="currentColor"`.

#### Usage

```tsx
import { Wordmark } from '@/components/common/Wordmark'

// Most contexts — let the component resolve theme automatically
<Wordmark />

// Force light palette (e.g. on a dark hero with brand bg)
<Wordmark variant="light" />

// Override size
<Wordmark className="h-6 w-auto" />
```

**Rules:**
- Always import from `@/components/common/Wordmark` — never inline the SVG in a new file.
- Do not pass `variant={resolvedTheme}` unless the parent has already called `useTheme` for another purpose. `'auto'` is the correct default for all common cases.
- Do not resize using `width`/`height` HTML attributes — use the `className` prop with a Tailwind `h-*` utility.

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

**Library:** `lucide-react` (currently `^0.400.0`; use the installed version and do not assume brand/logo icons exist)

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
- Never use hardcoded Flume palette colors in product components. Always use a CSS variable that has a dark mode value.
- Documented external brand surfaces, such as Telegram and WhatsApp in §8, are the only component-scoped color exceptions.
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

The repository has public marketing pages, an authenticated dashboard, and an admin surface. Keep feature-specific data logic near `lib/` and keep shared visual primitives in `components/`.

```
web/src/
├── components/
│   ├── common/       ← Wordmark, Navbar, Footer, shared public chrome
│   ├── landing/      ← public landing sections in render order
│   ├── bot/          ← bot page sections and Telegram simulation
│   ├── pricing/      ← pricing sections, comparison table, FAQ
│   ├── dashboard/    ← dashboard-only shared controls such as ApiKeySelector
│   └── ui/           ← Base UI/shadcn primitives; Button, Dialog, Table, etc.
│
├── pages/
│   ├── LandingPage.tsx
│   ├── BotPage.tsx
│   ├── PricingPage.tsx
│   ├── DocsPage.tsx
│   ├── dashboard/
│   │   ├── DashboardShell.tsx
│   │   ├── JobsPage.tsx
│   │   ├── JobDetailPage.tsx
│   │   ├── ApiKeysPage.tsx
│   │   ├── WebhooksPage.tsx
│   │   └── PlatformsPage.tsx
│   └── admin/        ← admin shell, login, and management pages
│
├── lib/
│   ├── tokens.css    ← all CSS variable values
│   ├── api.ts        ← authenticated HTTP client and refresh behavior
│   ├── jobs.ts       ← jobs API/types
│   ├── api-keys.ts   ← API key API/types
│   ├── webhooks.ts   ← webhook API/types
│   ├── platforms.ts  ← platform helpers/types
│   └── utils.ts      ← cn(), formatting helpers
│
├── hooks/            ← cross-page React hooks such as useTheme
├── stores/           ← Zustand global state such as auth and active API key
├── router/           ← React Router route tree
├── assets/           ← imported source assets
└── index.css         ← imports, @theme inline, layers, and custom utilities
```

Rules:

- Pages compose data and feature components; they should not become a second component library.
- Keep API request functions and response types in `lib/`, not inside JSX files.
- Keep global state minimal. Prefer component state for local dialogs, filters, and transient feedback.
- Add shared UI primitives to `components/ui/` only when at least two features need the same behavior or when the primitive is part of the shadcn/Base UI surface.
- Avoid importing a page-specific component into an unrelated feature solely to save lines.
- Update this tree when a new top-level architectural folder becomes part of the supported frontend pattern.

---

## 12 — Placeholders & Future Work

| File | Status | Note |
|---|---|---|
| `DemoPlaceholderSection.tsx` | ✅ Done | Telegram-simulated animated chat demo. See §6.8 for full documentation. |
| `PricingHero.tsx` | ⚠️ Placeholder data | Tier names, prices, and features are not final. See `// [PLACEHOLDER]` comment. |
| `ComparisonTable.tsx` | ⚠️ Placeholder data | Feature rows and tier limits are not final. See `// [PLACEHOLDER]` comment. |
| `PricingFAQ.tsx` | ⚠️ Placeholder data | FAQ copy reflects current policy assumptions. See `// [PLACEHOLDER]` comment. |
| `Footer.tsx` (WhatsApp link) | ⚠️ Dummy link | `https://wa.me/000000000` is a placeholder. Replace with real number before launch. |
| `BotHeroSection.tsx` (WhatsApp) | ⚠️ Dummy link | Same. |
| `PlatformsSection.tsx` (WhatsApp) | ⚠️ Coming soon | WhatsApp card is deliberately disabled (`opacity-75`, `pointer-events-none`). Enable when ready. |

---

## 13 — Adding a New Marketing Section (Checklist)

When adding a new public marketing section, verify every item:

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

### 13.1 Dashboard feature checklist

- [ ] Page uses the dashboard shell and does not introduce a second sidebar/header model.
- [ ] Page header has one `h1`, concrete copy, and one clear primary action when needed.
- [ ] Every query has loading, populated, empty, and recoverable error states.
- [ ] Loading skeletons mirror the final table/list/card anatomy.
- [ ] Mutations disable only the affected control and communicate pending/success/failure.
- [ ] Destructive actions use `AlertDialog` and identify the affected resource.
- [ ] Forms use shared primitives, associated labels, helper/error text, and keyboard-safe focus behavior.
- [ ] Technical values truncate or wrap without horizontal page overflow.
- [ ] Icon-only actions have labels, tooltips where useful, and application-size hit areas.
- [ ] Light mode, dark mode, narrow viewport, keyboard navigation, and reduced motion have been considered.

---

## 14 — Pricing Page Components

**Directory:** `web/src/components/pricing/`

The Pricing page is composed of three sections rendered in order: `PricingHero` → `ComparisonTable` → `PricingFAQ`. Billing period state is lifted to the page level and passed down.

```tsx
// Typical PricingPage composition
const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly')

<PricingHero billingPeriod={billingPeriod} onBillingPeriodChange={setBillingPeriod} />
<ComparisonTable billingPeriod={billingPeriod} />
<PricingFAQ />
```

---

### 14.1 PricingHero

**File:** `web/src/components/pricing/PricingHero.tsx`

Hero section for the pricing page. Combines a gradient hero header, a billing period toggle, and the three-tier pricing card grid.

#### Props

| Prop | Type | Description |
|---|---|---|
| `billingPeriod` | `'monthly' \| 'annual'` | Controls which price is shown in each tier card |
| `onBillingPeriodChange` | `(p: 'monthly' \| 'annual') => void` | Lifted state setter — called by billing toggle buttons |

#### Layout

- Section: `py-20 sm:py-28` + `gradient-hero` (hero variant — no eyebrow label)
- Inner header: `mb-12` (not `mb-14` — no subtext paragraph)
- Billing toggle: `inline-flex rounded-full bg-[var(--bg-subtle)] p-1 border border-[var(--border-subtle)]`; active state: `bg-[var(--bg-card)] shadow-sm`
- Tier grid: `grid-cols-1 md:grid-cols-3 gap-5 max-w-5xl mx-auto items-start`

#### `tiers` data shape

```ts
interface Tier {
  name: string
  monthly: { price: string; suffix: string }
  annual:  { price: string; suffix: string }
  annualSub: string | null          // shown below price when billingPeriod === 'annual'
  description: string
  features: string[]
  cta: string
  href: string
  highlighted: boolean              // only one tier may be true — triggers ring + scale treatment
}
```

Tier cards follow the §6.4 Pricing Tier Card pattern. The highlighted card uses `border-[var(--brand)] ring-1 ring-[var(--brand)] shadow-lg scale-[1.02]`. The "Recommended" badge (§6.5) is positioned `absolute -top-3 left-1/2 -translate-x-1/2`.

> ⚠️ `// [PLACEHOLDER]` — prices, features, and CTA links are not final.

---

### 14.2 ComparisonTable

**File:** `web/src/components/pricing/ComparisonTable.tsx`

A full-width feature comparison table across Free, Pro, and Enterprise tiers. Visually highlights the Pro column.

#### Props

| Prop | Type | Description |
|---|---|---|
| `billingPeriod` | `'monthly' \| 'annual'` | Drives the price row shown in the table header |

#### Data shapes

```ts
type CellValue = boolean | string

interface FeatureRow {
  label: string
  free: CellValue
  pro: CellValue
  enterprise: CellValue
}

interface FeatureGroup {
  category: string   // rendered as a full-width category header row
  rows: FeatureRow[]
}
```

`CellValue` rendering: `true` → `<Check h-4 w-4 text-brand>`, `false` → `<Minus h-4 w-4 text-[var(--text-muted)]>`, `string` → plain text.

#### Layout

- Section background: `bg-[var(--bg-subtle)]`
- Table container: `overflow-x-auto rounded-xl border border-[var(--border-subtle)]`; inner table: `min-w-[560px]` for horizontal scroll safety on mobile
- Pro column highlight: `bg-brand-light` on both the `<th>` header cell and every `<td>` data cell in the Pro column

> ⚠️ `// [PLACEHOLDER]` — feature rows and tier limits are not final.

---

### 14.3 PricingFAQ

**File:** `web/src/components/pricing/PricingFAQ.tsx`

Self-contained FAQ section using the base-ui-backed `Accordion`.

#### Props

None. The FAQ copy is hardcoded in the component.

#### Accordion notes

The `Accordion` in `web/src/components/ui/accordion.tsx` wraps `@base-ui/react/accordion`, **not** Radix UI. Base UI's accordion:
- Is always collapsible — do **not** pass a `collapsible` prop (it does not exist on the type and will cause TS2322).
- Uses `data-open` / `data-closed` attributes instead of Radix's `data-state`.

Each `AccordionItem` uses: `rounded-xl border border-(--border-subtle) bg-(--bg-card) px-6 not-last:border-b data-open:border-(--border-strong) transition-colors duration-200`.

> ⚠️ `// [PLACEHOLDER]` — FAQ copy reflects current policy assumptions and is not final.

---

## 15 — System Architecture & Sources of Truth

This document defines the product language and implementation rules. Keep the following ownership boundaries intact:

| Concern | Source of truth | Rule |
|---|---|---|
| Product visual language | `docs/design/design-system.md` | Document decisions and exceptions here before spreading them across pages. |
| CSS variable values | `web/src/lib/tokens.css` | Every custom token must have a light value in `:root` and a dark value in `.dark`. |
| Tailwind exposure and utilities | `web/src/index.css` | Expose tokens in `@theme inline`; put resets in `@layer base` and reusable classes in `@layer components` or `@utility`. |
| Component primitive configuration | `web/components.json` | Current configuration is `base-nova`, Base UI, Tailwind v4, Lucide, CSS variables, and `@/*` aliases. |
| Shared behavior primitives | `web/src/components/ui/` | Extend or compose existing primitives before creating a new local primitive. |
| Page composition | `web/src/pages/` and `web/src/components/` | Pages own data orchestration; shared components own reusable visual/interaction behavior. |
| API and query functions | `web/src/lib/` | Keep HTTP calls and response types out of presentational components. |
| Global client state | `web/src/stores/` | Use Zustand only for cross-route state such as auth and the active API key. |
| Server state | TanStack Query | Use query keys, mutations, invalidation, loading, error, and empty states consistently. |

### 15.1 Compatibility baseline

The current frontend baseline is:

- React `^19.0.0` with TypeScript `^5.6.0`.
- Vite `^6.0.0` with Tailwind CSS `^4.2.0` and `@tailwindcss/vite`.
- `shadcn` `^4.7.0` using `@base-ui/react` `^1.4.1`.
- TanStack Query `^5.60.0`, Zustand `^5.0.14`, Sonner `^1.7.0`, Framer Motion `^12.40.0`.
- `lucide-react` `^0.400.0`; use icons available in the installed version.
- `DM Sans` and `Instrument Serif` from `@fontsource` packages.

Do not add a package for a one-off visual need. If a package is required, check `web/package.json`, confirm Tailwind/Base UI compatibility, and update this section when the baseline changes.

### 15.2 Component selection order

1. Reuse an existing component from `web/src/components/`.
2. Compose the closest Base UI/shadcn primitive from `web/src/components/ui/`.
3. Add a new shared primitive only when the interaction model is genuinely missing.
4. Keep page-specific composition local when reuse would create an unrelated dependency.

Use the Base UI `render` prop for composition. Do not introduce Radix-specific APIs such as `asChild` into Base UI components.

---

## 16 — Application Shell & Page Anatomy

The dashboard is an operational application, not a marketing page. It follows a denser page pattern than §5.

### 16.1 Dashboard shell

`DashboardShell.tsx` is the shared shell for `/dashboard/*` routes:

```text
Desktop (md+)
┌────────────── 256px sidebar ──────────────┬────────────── main ──────────────┐
│ wordmark                                   │ main p-4 / p-6 / p-8              │
│ Development                               │ max-w-7xl mx-auto                  │
│ API-key selector                           │ page content                       │
│ Jobs / API Keys / Webhooks / Platforms     │                                     │
│ user + sign out                            │                                     │
└───────────────────────────────────────────┴─────────────────────────────────────┘

Mobile
┌──────────────────────── h-16 mobile header ────────────────────────┐
│ wordmark                                                   menu     │
└─────────────────────────────────────────────────────────────────────┘
│ page content with responsive padding                                  │
```

Rules:

- Desktop sidebar: `w-64`, sticky, full viewport height, card surface, subtle right border.
- Main content: `min-w-0`, responsive padding `p-4 sm:p-6 lg:p-8`, inner `max-w-7xl mx-auto`.
- Mobile header: `h-16`, sticky, card surface, subtle bottom border, Base UI `Sheet` for navigation.
- Navigation uses `Link` for internal routes and `<a>` for external routes.
- Active navigation uses `bg-brand/10 text-brand`; inactive navigation uses secondary text and subtle hover fill.
- Keep the sidebar structure stable. New dashboard work should not introduce a second navigation model.

### 16.2 Dashboard page header

Use a compact, left-aligned header. A typical page header is:

```tsx
<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
  <div>
    <h1 className="text-display text-3xl text-(--text-primary)">Page title</h1>
    <p className="mt-1 text-sm leading-relaxed text-(--text-secondary)">Specific supporting description.</p>
  </div>
  <Button>Primary action</Button>
</div>
```

Rules:

- Dashboard pages may omit an eyebrow. Do not add one only to satisfy marketing-section rules.
- Use `space-y-6` for compact tables and `space-y-8` for richer operational cards.
- Put page-level filters and actions in the header or an adjacent control row, not inside every data item.
- Use a single primary action per page header. Secondary actions use `outline`, `secondary`, or `ghost`.
- Keep titles concrete: `Webhooks`, `Jobs`, `API Keys`, `Supported Platforms`.

### 16.3 Narrow detail columns

Detail pages may use `max-w-4xl` or another narrower inner column when reading order benefits from it. This is an application-page exception, not a marketing-section container rule.

---

## 17 — Data, Query & State Patterns

Every async surface must define the full state model before implementation:

```text
loading → populated
        ↘ empty
        ↘ recoverable error → retry

mutation → pending → success toast + query invalidation
                 ↘ error toast + preserved user input
```

### 17.1 TanStack Query conventions

- Query keys include every filter, route parameter, and active API-key scope used by the request.
- Keep query functions in `web/src/lib/` and pass them to `useQuery` from the page.
- Use `isLoading` for first-load skeletons and `isFetching` for background refresh indicators.
- Use `queryClient.invalidateQueries` after mutations that affect a list or detail view.
- Preserve user input on mutation errors; do not silently reset a failed form.
- Display recoverable errors with a clear retry action whenever the query exposes `refetch`.
- Keep empty state copy specific to the current scope and give the next useful action.

### 17.2 Required states

| State | Visual treatment | Required behavior |
|---|---|---|
| Loading | Skeletons matching the final anatomy, not generic page-sized blocks | Keep layout stable and avoid content jumps. |
| Empty | One semantic Lucide icon in a brand-light container, short explanation, next action | Explain whether there is no data or no scope selected. |
| Error | Destructive/semantic callout with concise reason and retry | Do not expose raw stack traces or leave a dead end. |
| Populated | Use the appropriate table, list, timeline, or operational card pattern | Support truncation, wrapping, and long real-world values. |
| Mutating | Disable only the affected action and show an inline spinner or progress label | Keep unrelated page controls usable. |
| Success | Sonner toast plus updated local/query state | Use outcome-oriented copy such as `Endpoint added`. |

### 17.3 Status semantics

Use the existing semantic palette consistently:

- **Positive / active / succeeded:** `default` Badge or `text-brand` with `bg-brand/10`.
- **Neutral / pending / processing:** `secondary` or `outline` Badge.
- **Negative / failed / destructive:** `destructive` Badge or destructive callout.
- **Disabled / revoked:** `secondary`, muted text, and reduced emphasis without removing meaning.

Do not introduce orange, red, blue, or purple utility colors in product components. If a warning role is needed, add a named semantic token to `tokens.css` in both themes before using it.

---

## 18 — Tables, Lists & Operational Cards

### 18.1 Data tables

Use the shared `Table` primitives for comparable records such as jobs, API keys, and platforms:

```tsx
<div className="overflow-hidden rounded-xl border border-(--border-subtle) bg-(--bg-card)">
  <Table>
    <TableHeader>...</TableHeader>
    <TableBody>...</TableBody>
  </Table>
</div>
```

Rules:

- The shared `Table` provides horizontal overflow; do not use manual width arithmetic.
- Keep tables readable at mobile widths with overflow rather than collapsing unrelated columns into ambiguous labels.
- Table headers use concise sentence-case labels; monospace is appropriate for technical column names and identifiers.
- Use `TableRow` hover only for row-level scan feedback. Do not imply a row is clickable unless it is a link or has a clear action.
- Use skeleton rows with the same column count and rough widths as the populated table.
- Empty and error states should occupy a table row with the correct `colSpan`.
- Copy actions require an accessible label and visible copied feedback; do not use an unlabeled raw `<button>`.

### 18.2 Lists and delivery logs

Use a separator-based list when items are sequential activity or delivery attempts. Reserve nested bordered surfaces for meaningful callouts, not every row.

Each operational row should answer, in order:

1. What happened? — event, job, or resource name.
2. When? — relative time, with an absolute value available to a tooltip/title if needed.
3. What was the result? — status and response code.
4. What can I do? — a clear row action if one exists.

Use monospace for URLs, IDs, event types, HTTP codes, and response bodies. Use `truncate`, `break-all`, or responsive wrapping so long technical values never expand the page horizontally.

### 18.3 Cards and nesting

- Use a card when it creates a meaningful surface boundary or groups a coherent operational object.
- Prefer borders, separators, and whitespace for subregions inside a card.
- Avoid card-inside-card repetition. A status callout, form section, or empty activity panel may use a distinct surface only when its semantics justify it.
- Do not add hover elevation to a static container. Hover depth is reserved for a card that is itself interactive or contains a clearly interactive surface.
- Interactive cards use `hover:border-(--border-strong) hover:shadow-sm transition-all duration-200`.

---

## 19 — Forms, Dialogs & Destructive Actions

### 19.1 Form fields

Use the shared `Label`, `Input`, `Select`, `Checkbox`, `Switch`, and `Textarea` primitives. Every field must have:

- A visible label associated with its control using `htmlFor`/`id` or a documented Base UI field relationship.
- Helper text when format, security, or side effects need explanation.
- `aria-describedby` for helper or error text.
- A stable focus ring and a logical keyboard order.
- A clear disabled/loading state during submission.
- Validation on blur and submit by default; errors should be adjacent to the affected field.

Do not use placeholder text as the only label. Do not use a raw HTML checkbox, select, or button when an existing primitive provides the interaction.

### 19.2 Dialog anatomy

```tsx
<Dialog open={open} onOpenChange={setOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle className="text-display text-2xl">Outcome-oriented title</DialogTitle>
      <DialogDescription>What the form changes and any important constraint.</DialogDescription>
    </DialogHeader>
    <div className="space-y-6 py-2">Form fields</div>
    <DialogFooter>
      <Button variant="outline">Cancel</Button>
      <Button>Save changes</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

Rules:

- Dialogs use `max-w-[calc(100%-2rem)]` through the shared primitive and remain usable on narrow screens.
- Use sentence-case titles and outcome-oriented actions: `Add endpoint`, `Save changes`, `Delete endpoint`, `Keep endpoint`.
- Keep the primary action disabled only when the required data is invalid or the mutation is pending.
- Use `AlertDialog` for irreversible actions. State exactly what will be deleted/revoked and name the affected resource.
- One-time secrets/keys must use a deliberate acknowledgement gate, copy feedback, and a warning that the value cannot be recovered.
- Never nest interactive buttons. Compose triggers with Base UI `render` instead.

### 19.3 Toggle controls

Use `Switch` for an immediate boolean setting such as endpoint enablement. The switch must have:

- A stable `id`.
- An associated visible `Label` when adjacent text describes the setting.
- A descriptive `aria-label` when there is no visible label.
- A pending state that prevents duplicate mutations.
- A success/error toast or inline feedback after the server response.

---

## 20 — Responsive & Accessibility Contract

Responsive behavior is part of the component contract, not a final polish pass.

### 20.1 Responsive rules

- Use mobile-first classes and allow controls to wrap; do not force a desktop action cluster into a narrow row.
- Give non-full-width containers a sensible `min-width`/`max-width` relationship and keep `min-w-0` on flex children containing technical text.
- Use horizontal overflow for wide data tables and wrapping/truncation for URLs, IDs, and source URIs.
- Maintain at least a 44px visual or hit-area target for icon-only actions on application surfaces. The shared Button `icon` size is 32px, so use an explicit `size-11` hit area when the control is exposed to touch.
- Dialog footers stack on small screens through the shared `DialogFooter`; do not create fixed-width actions that overflow.
- Use `min-h-[100dvh]` for full-screen page designs; avoid `h-screen` when building new viewport layouts.

### 20.2 Accessibility rules

- Use semantic headings in order. A page has one `h1`; empty/error/detail sections use the next appropriate heading level.
- Icon-only controls require `aria-label`; decorative icons require `aria-hidden="true"`.
- Tooltips supplement labels; they never replace accessible names.
- Use `role="status"` and `aria-live="polite"` for async test/result feedback when appropriate.
- Keep destructive actions keyboard reachable and confirmation dialogs focus-managed by the Base UI primitive.
- Never rely on color alone for status. Pair color with text, an icon, or a status label.
- Respect reduced-motion preferences for new Framer Motion or CSS animations. Do not animate layout properties such as `width`, `height`, `top`, or `left`.
- Test keyboard focus, Escape dismissal, outside-click behavior, and focus return for every new dialog, sheet, menu, select, and tooltip.

---

## 21 — Motion & Feedback

Motion should clarify state changes, not decorate a dashboard.

- Use the existing Base UI open/close data attributes for dialogs, sheets, accordions, selects, and tooltips.
- Use short `transition-colors`, `transition-opacity`, or `transition-transform` transitions for local feedback.
- Use Framer Motion only for intentional sequences or product demonstrations, such as the Telegram demo documented in §6.8.
- Prefer spring or deliberate cubic-bezier easing over linear motion.
- Never animate a data table row's layout while data is loading; use stable skeletons instead.
- Every mutation should communicate pending, success, and failure without requiring the user to infer what happened.

---

## 22 — Content & Copy System

- Use sentence case for normal UI labels, buttons, descriptions, table headers, and empty/error copy.
- Reserve uppercase tracked text for short atomic labels, status badges, or the `.text-label` eyebrow utility.
- Use concrete verbs and objects: `Add endpoint`, `Send test event`, `Save changes`, `Delete endpoint`.
- Keep technical values exact and monospace: URLs, API-key prefixes, job IDs, event names, HTTP codes, and response bodies.
- Empty states answer what is missing and what the user can do next.
- Error states explain recovery without exposing implementation details.
- Success toasts describe the completed outcome, not the internal mutation name.
- Do not use placeholder names, invented metrics, or vague marketing filler in application surfaces.

---

## 23 — Token & Component Contribution Workflow

Before adding a token:

1. Check whether an existing semantic token already expresses the role.
2. If not, add a descriptive CSS variable to both `:root` and `.dark` in `web/src/lib/tokens.css`.
3. Add the corresponding `--color-*` or font/radius mapping to `@theme inline` in `web/src/index.css` when a Tailwind utility needs it.
4. Document the token's role, contrast intent, and allowed contexts in §2.
5. Replace hardcoded usages in the affected component rather than adding a parallel one-off value.

Before adding a component:

1. Search `web/src/components/ui/` and `web/src/components/` for an existing match.
2. Read the primitive's actual props and composition API; Base UI is not Radix.
3. Define loading, empty, error, disabled, hover, focus, active, and destructive states where applicable.
4. Add labels, descriptions, keyboard behavior, responsive behavior, and dark-mode behavior before considering visual polish complete.
5. Update this document only for reusable patterns, not for incidental page copy.

Before merging a UI change:

- [ ] `npm run lint` passes in `web/`.
- [ ] `npm run build` passes in `web/`.
- [ ] `git diff --check` passes.
- [ ] Light and dark token values were reviewed.
- [ ] Desktop, narrow/mobile, keyboard, and reduced-motion behavior were considered.
- [ ] All async states and destructive flows were exercised or deliberately documented.
- [ ] Any exception to this document is recorded next to the component and summarized here if it becomes reusable.

---

## 24 — Canonical Operational Feature Patterns

The webhook page is the reference implementation for a resource that combines a server-backed collection, inline operations, a form, a one-time secret, and activity history.

### 24.1 Endpoint/resource card

Use this anatomy for callback endpoints, integrations, and similar operational resources:

```text
Resource surface
├── Identity: semantic icon + technical name/URL + scope/context
├── State: text status badge + immediate toggle when supported
├── Actions: primary test/sync action, edit, destructive action
├── Scope: event/type/tag chips with a readable all-items treatment
├── Feedback: inline success/failure result with status code/body when relevant
└── Activity: expandable separator-based recent history
```

Rules:

- Keep resource identity visually stronger than secondary metadata.
- Use `Webhook`, `Send`, `ShieldCheck`, `CheckCircle2`, `CircleX`, `Pencil`, and `Trash2`-style semantic Lucide icons where the installed version supports them; do not use a decorative icon without a product meaning.
- A status toggle is an immediate mutation. Disable only that control while pending and invalidate the scoped query after success.
- Test/sync actions show inline pending feedback and a result with both a human-readable outcome and technical detail.
- Destructive actions use `AlertDialog` and include the exact affected URL/name in the description.
- Activity history uses `formatRelativeTime` for scanability and preserves response/status/attempt metadata for debugging.

### 24.2 Empty, error, and loading examples

```tsx
// Loading: mirror the final resource anatomy.
<WebhookCardSkeleton />

// Empty: explain scope + next step.
<EmptyState icon={<Webhook />} title="No endpoints configured" action="Add endpoint" />

// Error: explain recovery.
<ErrorState title="Endpoints could not be loaded" action="Try again" />
```

Do not reuse this exact copy blindly. Keep the structure and write copy for the resource being managed.

### 24.3 One-time secret pattern

A secret/key reveal flow must:

1. Show the value in a selectable, wrapping monospace block.
2. Provide a labeled copy action with copied feedback.
3. State that the value will not be shown again.
4. Require explicit acknowledgement before dismissal when loss is irreversible.
5. Use a semantic warning treatment without introducing a new untracked accent color.

## 25 — Known Design-System Debt

The current repository still has implementation drift that should be addressed in future focused passes:

- Several older dashboard/admin pages use raw `<button>` elements for copy actions and the deprecated `icon-sm` size instead of the 44px application hit-area convention.
- Some existing pages use arbitrary `orange-*`, `red-*`, `black/*`, or `white/*` utilities for status and warning colors instead of semantic tokens.
- `ApiKeysPage.tsx` and parts of the admin UI use raw labels/checkboxes and have older one-time-secret styling that should converge on the shared dialog/form pattern.
- `PlatformsPage.tsx` and `JobsPage.tsx` use highly compressed 9–10px uppercase table metadata; use the table rules in §18 when those pages are next refined.
- The design system currently documents both legacy bracket-style variable utilities and Tailwind v4 parenthesis syntax in older examples. New code must use parenthesis syntax; migrate examples opportunistically.
- Browser-level visual regression coverage is not yet automated. Until it exists, final UI review should include light/dark and narrow viewport screenshots.

These are tracked follow-up items, not reasons to introduce exceptions in new work.
