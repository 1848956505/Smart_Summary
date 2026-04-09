/**
 * Theme palette and report style presets.
 */
import { Message, Document, ChatLineRound } from '@element-plus/icons-vue'

export const themes = {
  dingtalk: {
    name: '钉钉风格',
    primary: '#2563eb',
    primaryGradient: 'linear-gradient(135deg, #2563eb, #38bdf8)',
    background: 'rgba(37, 99, 235, 0.1)',
    border: 'rgba(37, 99, 235, 0.2)',
    shadow: 'rgba(37, 99, 235, 0.2)',
    text: '#0f172a',
    textSecondary: '#475569',
    accent: '#38bdf8'
  },
  feishu: {
    name: '飞书风格',
    primary: '#5b5fe0',
    primaryGradient: 'linear-gradient(135deg, #5b5fe0, #7c3aed)',
    background: 'rgba(91, 95, 224, 0.1)',
    border: 'rgba(91, 95, 224, 0.2)',
    shadow: 'rgba(91, 95, 224, 0.2)',
    text: '#111827',
    textSecondary: '#4b5563',
    accent: '#a78bfa'
  },
  wechat: {
    name: '企业微信风格',
    primary: '#0ea5a4',
    primaryGradient: 'linear-gradient(135deg, #0ea5a4, #22c55e)',
    background: 'rgba(14, 165, 164, 0.1)',
    border: 'rgba(14, 165, 164, 0.2)',
    shadow: 'rgba(14, 165, 164, 0.2)',
    text: '#111827',
    textSecondary: '#475569',
    accent: '#22c55e'
  }
}

export const styleOptions = [
  { label: '钉钉', value: 'dingtalk', icon: Message },
  { label: '飞书', value: 'feishu', icon: Document },
  { label: '企业微信', value: 'wechat', icon: ChatLineRound }
]

export function getTheme(style = 'dingtalk') {
  return themes[style] || themes.dingtalk
}

export function injectThemeVariables(style = 'dingtalk') {
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
