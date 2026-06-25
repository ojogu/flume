import { Resvg } from '@resvg/resvg-js'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const W = 1200
const H = 630

const BG = '#0C0C0E'
const BRAND = '#1D9E75'
const BRAND_MID = '#9FE1CB'
const BRAND_LIGHT_RGB = '29,158,117'
const TEXT_MUTED = '#5A5A72'

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
  <defs>
    <radialGradient id="glow" cx="50%" cy="25%" r="55%">
      <stop offset="0%" stop-color="rgba(${BRAND_LIGHT_RGB},0.07)" />
      <stop offset="100%" stop-color="rgba(${BRAND_LIGHT_RGB},0)" />
    </radialGradient>
  </defs>

  <rect width="${W}" height="${H}" fill="${BG}" />
  <rect width="${W}" height="${H}" fill="url(#glow)" />

  <!-- Wordmark mark: 3 parallelogram stripes -->
  <g transform="translate(476, 115) scale(8)">
    <path fill="rgba(${BRAND_LIGHT_RGB},0.25)" d="M0 11 L8 5 L26 5 L18 11 Z" />
    <path fill="${BRAND_MID}"  d="M0 19 L8 13 L26 13 L18 19 Z" />
    <path fill="${BRAND}"     d="M0 27 L8 21 L26 21 L18 27 Z" />
  </g>

  <!-- "flume" logotype -->
  <text x="600" y="350"
    text-anchor="middle"
    font-family="Georgia, 'Times New Roman', serif"
    font-style="italic"
    font-weight="400"
    font-size="82"
    letter-spacing="-3"
    fill="${BRAND_MID}">flume</text>

  <!-- Tagline -->
  <text x="600" y="420"
    text-anchor="middle"
    font-family="'Helvetica Neue', Helvetica, Arial, sans-serif"
    font-weight="400"
    font-size="20"
    letter-spacing="3"
    fill="${TEXT_MUTED}">Media Processing infrastructure</text>
</svg>`

const resvg = new Resvg(svg, { fitTo: { mode: 'original' } })
const pngBuffer = resvg.render().asPng()

const out = path.resolve(__dirname, '../public/og-image.png')
fs.writeFileSync(out, pngBuffer)
console.log(`✅ Generated ${out}  (${(pngBuffer.length / 1024).toFixed(1)} KB)`)
