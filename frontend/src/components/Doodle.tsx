/** 手绘线条图标（内联 SVG 涂鸦，2.2px 圆头描边，与墨线边框同气质） */

const S = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2.2,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
}

export const DoodleLog = () => (
  <svg className="tile-icon" viewBox="0 0 48 48" {...S}>
    <path d="M10 8h22l6 6v26H10z" /><path d="M32 8v6h6" />
    <path d="M16 20h14M16 26h14M16 32h9" />
  </svg>
)

export const DoodleWrite = () => (
  <svg className="tile-icon" viewBox="0 0 48 48" {...S}>
    <path d="M8 40l6-2L38 14l-6-6L10 32l-2 8z" /><path d="M28 12l6 6" />
  </svg>
)

export const DoodleMine = () => (
  <svg className="tile-icon" viewBox="0 0 48 48" {...S}>
    <rect x="8" y="10" width="30" height="30" rx="4" /><path d="M14 20h18M14 27h12" />
  </svg>
)

export const DoodleAbout = () => (
  <svg className="tile-icon" viewBox="0 0 48 48" {...S}>
    <circle cx="24" cy="16" r="7" /><path d="M12 40c2-9 7-13 12-13s10 4 12 13" />
  </svg>
)

export const DoodleLogin = () => (
  <svg className="tile-icon" viewBox="0 0 48 48" {...S}>
    <path d="M28 8h12v32H28" /><path d="M6 24h22M22 17l7 7-7 7" />
  </svg>
)

export const DoodleHome = () => (
  <svg className="tile-icon" viewBox="0 0 48 48" {...S}>
    <path d="M6 24L24 8l18 16" /><path d="M11 22v18h26V22" /><path d="M20 40v-10h8v10" />
  </svg>
)
