import { Link } from 'react-router-dom'
import { PlusCircle, Video, Eye, ThumbsUp } from 'lucide-react'

const stats = [
  { label: 'Total Videos', value: '0', icon: Video, color: 'bg-blue-50 text-blue-600' },
  { label: 'Total Views', value: '0', icon: Eye, color: 'bg-green-50 text-green-600' },
  { label: 'Total Likes', value: '0', icon: ThumbsUp, color: 'bg-purple-50 text-purple-600' },
]

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500">Welcome to Gase-Y Pipeline</p>
        </div>
        <Link
          to="/create"
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700"
        >
          <PlusCircle className="h-4 w-4" />
          Create Video
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-xl border border-gray-200 bg-white p-6">
            <div className="flex items-center gap-4">
              <div className={`rounded-lg p-3 ${stat.color}`}>
                <stat.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-8 text-center">
        <Video className="mx-auto h-12 w-12 text-gray-300" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">No videos yet</h3>
        <p className="mt-2 text-sm text-gray-500">
          Create your first video by entering a prompt
        </p>
        <Link
          to="/create"
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <PlusCircle className="h-4 w-4" />
          Get Started
        </Link>
      </div>
    </div>
  )
}
