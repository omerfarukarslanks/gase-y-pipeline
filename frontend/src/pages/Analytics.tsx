import { BarChart3 } from 'lucide-react'

export default function Analytics() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>

      <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
        <BarChart3 className="mx-auto h-12 w-12 text-gray-300" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">No analytics data yet</h3>
        <p className="mt-2 text-sm text-gray-500">
          Analytics will appear here after you publish videos to social platforms.
        </p>
      </div>
    </div>
  )
}
