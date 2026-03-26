interface PlatformStat {
  platform: string
  videos: number
  views: number
  likes: number
}

export default function PlatformStats({ stats }: { stats: PlatformStat[] }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6">
      <h3 className="mb-4 text-sm font-medium text-gray-700">Platform Performance</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="pb-3 text-left font-medium text-gray-500">Platform</th>
              <th className="pb-3 text-right font-medium text-gray-500">Videos</th>
              <th className="pb-3 text-right font-medium text-gray-500">Views</th>
              <th className="pb-3 text-right font-medium text-gray-500">Likes</th>
            </tr>
          </thead>
          <tbody>
            {stats.map((stat) => (
              <tr key={stat.platform} className="border-b border-gray-50">
                <td className="py-3 font-medium capitalize">{stat.platform}</td>
                <td className="py-3 text-right text-gray-600">{stat.videos}</td>
                <td className="py-3 text-right text-gray-600">{stat.views.toLocaleString()}</td>
                <td className="py-3 text-right text-gray-600">{stat.likes.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
