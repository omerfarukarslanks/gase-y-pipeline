import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  CalendarDays, ChevronLeft, ChevronRight,
  Clock, CheckCircle, XCircle, Loader2, ExternalLink,
} from 'lucide-react'
import { calendarApi } from '../api/analytics'
import type { CalendarEvent } from '../api/analytics'

const PLATFORM_COLORS: Record<string, string> = {
  youtube: 'border-l-red-500',
  instagram: 'border-l-pink-500',
  twitter: 'border-l-sky-500',
  tiktok: 'border-l-gray-700',
  reddit: 'border-l-orange-500',
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  published: <CheckCircle className="h-3.5 w-3.5 text-green-500" />,
  failed: <XCircle className="h-3.5 w-3.5 text-red-500" />,
  scheduled: <Clock className="h-3.5 w-3.5 text-amber-500" />,
  pending: <Clock className="h-3.5 w-3.5 text-gray-400" />,
  publishing: <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-500" />,
}

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null)

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()

  // Get date range for current month view
  const startOfMonth = new Date(year, month, 1)
  const endOfMonth = new Date(year, month + 1, 0, 23, 59, 59)

  const { data, isLoading } = useQuery({
    queryKey: ['calendar-events', year, month, selectedPlatform],
    queryFn: () =>
      calendarApi.events({
        start: startOfMonth.toISOString(),
        end: endOfMonth.toISOString(),
        platform: selectedPlatform || undefined,
      }),
    select: (res) => res.data,
  })

  const events = data?.events || []

  // Group events by date
  const eventsByDate = useMemo(() => {
    const map: Record<string, CalendarEvent[]> = {}
    for (const event of events) {
      if (!event.date) continue
      const dateKey = event.date.split('T')[0]
      if (!map[dateKey]) map[dateKey] = []
      map[dateKey].push(event)
    }
    return map
  }, [events])

  // Build calendar grid
  const calendarDays = useMemo(() => {
    const firstDay = startOfMonth.getDay()
    // Adjust for Monday start (0 = Mon)
    const startOffset = firstDay === 0 ? 6 : firstDay - 1
    const daysInMonth = endOfMonth.getDate()

    const days: Array<{ day: number | null; dateKey: string }> = []

    // Padding before
    for (let i = 0; i < startOffset; i++) {
      days.push({ day: null, dateKey: '' })
    }
    // Actual days
    for (let d = 1; d <= daysInMonth; d++) {
      const dateKey = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
      days.push({ day: d, dateKey })
    }
    return days
  }, [year, month])

  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1))
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1))
  const goToday = () => setCurrentDate(new Date())

  const todayKey = new Date().toISOString().split('T')[0]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Content Calendar</h1>
          <p className="text-sm text-gray-500">
            {events.length} event{events.length !== 1 ? 's' : ''} this month
          </p>
        </div>

        {/* Platform filter */}
        <div className="flex items-center gap-2">
          {['youtube', 'instagram', 'twitter', 'tiktok', 'reddit'].map((p) => (
            <button
              key={p}
              onClick={() => setSelectedPlatform(p === selectedPlatform ? null : p)}
              className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors ${
                selectedPlatform === p
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Month navigation */}
      <div className="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-5 py-3">
        <button onClick={prevMonth} className="rounded-lg p-1 hover:bg-gray-100">
          <ChevronLeft className="h-5 w-5 text-gray-600" />
        </button>
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-gray-900">
            {MONTHS[month]} {year}
          </h2>
          <button
            onClick={goToday}
            className="rounded-md bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700 hover:bg-brand-100"
          >
            Today
          </button>
        </div>
        <button onClick={nextMonth} className="rounded-lg p-1 hover:bg-gray-100">
          <ChevronRight className="h-5 w-5 text-gray-600" />
        </button>
      </div>

      {/* Calendar grid */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        {/* Day headers */}
        <div className="grid grid-cols-7 border-b border-gray-200 bg-gray-50">
          {DAYS.map((day) => (
            <div key={day} className="px-2 py-2 text-center text-xs font-medium text-gray-500">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar cells */}
        <div className="grid grid-cols-7">
          {calendarDays.map((cell, i) => {
            const dayEvents = cell.dateKey ? eventsByDate[cell.dateKey] || [] : []
            const isToday = cell.dateKey === todayKey

            return (
              <div
                key={i}
                className={`min-h-[100px] border-b border-r border-gray-100 p-1.5 ${
                  cell.day === null ? 'bg-gray-50' : ''
                }`}
              >
                {cell.day !== null && (
                  <>
                    <div
                      className={`mb-1 text-xs font-medium ${
                        isToday
                          ? 'flex h-6 w-6 items-center justify-center rounded-full bg-brand-600 text-white'
                          : 'text-gray-500'
                      }`}
                    >
                      {cell.day}
                    </div>
                    <div className="space-y-0.5">
                      {dayEvents.slice(0, 3).map((event) => (
                        <div
                          key={event.id}
                          className={`flex items-center gap-1 rounded border-l-2 bg-gray-50 px-1.5 py-0.5 text-[10px] ${
                            PLATFORM_COLORS[event.platform] || 'border-l-gray-300'
                          }`}
                          title={`${event.title} (${event.platform} - ${event.status})`}
                        >
                          {STATUS_ICONS[event.status]}
                          <span className="truncate text-gray-700">{event.title || 'Untitled'}</span>
                        </div>
                      ))}
                      {dayEvents.length > 3 && (
                        <p className="text-[10px] text-gray-400 pl-1">
                          +{dayEvents.length - 3} more
                        </p>
                      )}
                    </div>
                  </>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Upcoming events list */}
      {events.filter((e) => e.status === 'scheduled').length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h3 className="mb-3 text-sm font-medium text-gray-700">
            <Clock className="mr-1.5 inline h-4 w-4" />
            Upcoming Scheduled
          </h3>
          <div className="space-y-2">
            {events
              .filter((e) => e.status === 'scheduled')
              .sort((a, b) => (a.scheduled_at || '').localeCompare(b.scheduled_at || ''))
              .slice(0, 10)
              .map((event) => (
                <div
                  key={event.id}
                  className={`flex items-center justify-between rounded-lg border-l-2 bg-gray-50 px-3 py-2 text-sm ${
                    PLATFORM_COLORS[event.platform] || 'border-l-gray-300'
                  }`}
                >
                  <div>
                    <span className="font-medium text-gray-900">{event.title || 'Untitled'}</span>
                    <span className="ml-2 text-xs text-gray-500 capitalize">{event.platform}</span>
                    <span className="ml-1 text-xs text-gray-400">({event.language.toUpperCase()})</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {event.scheduled_at
                      ? new Date(event.scheduled_at).toLocaleString()
                      : ''}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
