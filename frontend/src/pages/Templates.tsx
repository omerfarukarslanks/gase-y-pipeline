import { LayoutTemplate } from 'lucide-react'

const sampleTemplates = [
  { id: '1', name: 'Educational', category: 'education', desc: 'Perfect for tutorials and explainers' },
  { id: '2', name: 'Product Showcase', category: 'product', desc: 'Highlight your product features' },
  { id: '3', name: 'News Update', category: 'news', desc: 'Quick news and updates format' },
  { id: '4', name: 'Motivational', category: 'motivation', desc: 'Inspiring quotes and stories' },
]

export default function Templates() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Templates</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {sampleTemplates.map((tmpl) => (
          <div
            key={tmpl.id}
            className="cursor-pointer rounded-xl border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md"
          >
            <div className="mb-3 flex h-32 items-center justify-center rounded-lg bg-gray-50">
              <LayoutTemplate className="h-10 w-10 text-gray-300" />
            </div>
            <h3 className="text-sm font-medium text-gray-900">{tmpl.name}</h3>
            <p className="mt-1 text-xs text-gray-500">{tmpl.desc}</p>
            <span className="mt-2 inline-block rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
              {tmpl.category}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
