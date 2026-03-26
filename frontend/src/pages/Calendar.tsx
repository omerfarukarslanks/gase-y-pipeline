import { CalendarDays } from 'lucide-react'

export default function Calendar() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Content Calendar</h1>

      <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
        <CalendarDays className="mx-auto h-12 w-12 text-gray-300" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">Content calendar coming soon</h3>
        <p className="mt-2 text-sm text-gray-500">
          Schedule and manage your video publishing from here.
        </p>
      </div>
    </div>
  )
}
