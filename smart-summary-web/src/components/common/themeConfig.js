/**
 * Theme palette and report style presets.
 */
import { Grid, Tickets } from '@element-plus/icons-vue'

export const themes = {
  list: {
    name: '列表风格',
    primary: '#4f46e5',
    primaryGradient: 'linear-gradient(135deg, #4f46e5, #7c3aed)',
    background: 'rgba(79, 70, 229, 0.1)',
    border: 'rgba(79, 70, 229, 0.24)',
    shadow: 'rgba(79, 70, 229, 0.2)',
    text: '#111827',
    textSecondary: '#475569',
    accent: '#a855f7'
  },
  table: {
    name: '表格风格',
    primary: '#6366f1',
    primaryGradient: 'linear-gradient(135deg, #6366f1, #9333ea)',
    background: 'rgba(99, 102, 241, 0.1)',
    border: 'rgba(99, 102, 241, 0.24)',
    shadow: 'rgba(99, 102, 241, 0.2)',
    text: '#0f172a',
    textSecondary: '#475569',
    accent: '#c084fc'
  }
}

export const styleOptions = [
  { label: '列表', value: 'list', icon: Tickets },
  { label: '表格', value: 'table', icon: Grid }
]

export function normalizeStyle(style = 'list') {
  const value = String(style || '').trim().toLowerCase()
  if (value === 'table' || value === '表格') return 'table'
  if (value === 'list' || value === '列表') return 'list'
  if (['dingtalk', '钉钉', 'feishu', '飞书', 'wechat', 'wechatwork', '企微', '企业微信'].includes(value)) return 'list'
  return 'list'
}

export function getTheme(style = 'list') {
  return themes[normalizeStyle(style)] || themes.list
}

export function getStyleLabel(style = 'list') {
  return normalizeStyle(style) === 'table' ? '表格' : '列表'
}

export function injectThemeVariables(style = 'list') {
  const theme = getTheme(style)
  const root = document.documentElement

  root.style.setProperty('--theme-primary', theme.primary)
  root.style.setProperty('--theme-primary-gradient', theme.primaryGradient)
  root.style.setProperty('--theme-background', theme.background)
  root.style.setProperty('--theme-border', theme.border)
  root.style.setProperty('--theme-shadow', theme.shadow)
  root.style.setProperty('--theme-text', theme.text)
  root.style.setProperty('--theme-text-secondary', theme.textSecondary)
  root.style.setProperty('--theme-accent', theme.accent)
}
