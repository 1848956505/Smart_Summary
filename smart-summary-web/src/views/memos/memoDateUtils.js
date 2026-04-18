export const formatLocalDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export const parseLocalDate = (dateStr) => {
  const [y, m, d] = dateStr.split('-').map(Number)
  return new Date(y, m - 1, d)
}

export const buildWeekDayItems = (week) => {
  if (!week?.weekStartDate) return []
  const start = parseLocalDate(week.weekStartDate)
  if (Number.isNaN(start.getTime())) return []

  const labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const prefixes = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

  return Array.from({ length: 7 }).map((_, idx) => {
    const d = new Date(start)
    d.setDate(start.getDate() + idx)
    return {
      date: formatLocalDate(d),
      label: labels[idx],
      prefix: prefixes[idx]
    }
  })
}

export const getDefaultWeekDate = (week) => {
  const items = buildWeekDayItems(week)
  if (!items.length) {
    return formatLocalDate(new Date())
  }
  const weekdayIndex = (new Date().getDay() + 6) % 7
  return items[weekdayIndex]?.date || items[0].date
}

export const getDefaultWeekRange = () => {
  const now = new Date()
  const day = now.getDay() || 7
  const monday = new Date(now)
  monday.setDate(now.getDate() - day + 1)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  return {
    weekStartDate: formatLocalDate(monday),
    weekEndDate: formatLocalDate(sunday)
  }
}

export const getCurrentWeekMonday = () => {
  const now = new Date()
  const day = now.getDay() || 7
  const monday = new Date(now)
  monday.setDate(now.getDate() - day + 1)
  monday.setHours(0, 0, 0, 0)
  return monday
}
