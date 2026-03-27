import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { LayoutTemplate, Copy, Trash2, Plus, Loader2, Lock } from 'lucide-react'
import { toast } from 'sonner'
import { templatesApi } from '../api/templates'
import { useVideoStore } from '../stores/videoStore'
import type { Template } from '../types/video'

const CATEGORY_COLORS: Record<string, string> = {
  education: 'bg-blue-100 text-blue-700',
  product: 'bg-green-100 text-green-700',
  news: 'bg-red-100 text-red-700',
  motivation: 'bg-purple-100 text-purple-700',
  entertainment: 'bg-yellow-100 text-yellow-700',
  tutorial: 'bg-indigo-100 text-indigo-700',
}

export default function Templates() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const setAspectRatio = useVideoStore((s) => s.setAspectRatio)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const { data: templates = [], isLoading } = useQuery({
    queryKey: ['templates', selectedCategory],
    queryFn: () => templatesApi.list(selectedCategory || undefined),
    select: (res) => res.data,
  })

  const { data: categoriesData } = useQuery({
    queryKey: ['template-categories'],
    queryFn: () => templatesApi.categories(),
    select: (res) => res.data,
  })

  const duplicateMutation = useMutation({
    mutationFn: (id: string) => templatesApi.duplicate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      toast.success('Template duplicated')
    },
    onError: () => toast.error('Failed to duplicate template'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => templatesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] })
      toast.success('Template deleted')
    },
    onError: () => toast.error('Failed to delete template'),
  })

  const handleUseTemplate = (template: Template) => {
    // Apply template's default settings to video store
    const defaults = template.default_settings || {}
    if (defaults.aspect_ratio) {
      setAspectRatio(defaults.aspect_ratio as string)
    }
    // Navigate to create page with template context
    navigate(`/create?template=${template.id}`)
  }

  const handleDelete = (template: Template) => {
    if (window.confirm(`Delete "${template.name}"?`)) {
      deleteMutation.mutate(template.id)
    }
  }

  const categories = categoriesData?.categories || []
  const systemTemplates = templates.filter((t) => t.is_system)
  const userTemplates = templates.filter((t) => !t.is_system)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Templates</h1>
          <p className="text-sm text-gray-500">Choose a template to speed up video creation</p>
        </div>
        <button
          onClick={() => navigate('/create')}
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          <Plus className="h-4 w-4" />
          Start from Scratch
        </button>
      </div>

      {/* Category filter */}
      {categories.length > 0 && (
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              !selectedCategory
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat === selectedCategory ? null : cat)}
              className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors ${
                selectedCategory === cat
                  ? 'bg-gray-900 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      ) : (
        <>
          {/* System Templates */}
          {systemTemplates.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                System Templates
              </h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {systemTemplates.map((tmpl) => (
                  <TemplateCard
                    key={tmpl.id}
                    template={tmpl}
                    onUse={() => handleUseTemplate(tmpl)}
                    onDuplicate={() => duplicateMutation.mutate(tmpl.id)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* User Templates */}
          {userTemplates.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                My Templates
              </h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {userTemplates.map((tmpl) => (
                  <TemplateCard
                    key={tmpl.id}
                    template={tmpl}
                    onUse={() => handleUseTemplate(tmpl)}
                    onDuplicate={() => duplicateMutation.mutate(tmpl.id)}
                    onDelete={() => handleDelete(tmpl)}
                  />
                ))}
              </div>
            </div>
          )}

          {templates.length === 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
              <LayoutTemplate className="mx-auto h-12 w-12 text-gray-300" />
              <p className="mt-4 text-gray-500">No templates found</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function TemplateCard({
  template,
  onUse,
  onDuplicate,
  onDelete,
}: {
  template: Template
  onUse: () => void
  onDuplicate: () => void
  onDelete?: () => void
}) {
  const catColor = CATEGORY_COLORS[template.category || ''] || 'bg-gray-100 text-gray-600'
  const sceneCount = (template.scene_structure as Record<string, unknown>)?.scenes
    ? (((template.scene_structure as Record<string, unknown>).scenes) as unknown[]).length
    : null

  return (
    <div className="group relative rounded-xl border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md">
      {/* Preview area */}
      <div className="mb-3 flex h-28 items-center justify-center rounded-lg bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="text-center">
          <LayoutTemplate className="mx-auto h-8 w-8 text-gray-300" />
          {sceneCount && (
            <p className="mt-1 text-[10px] text-gray-400">{sceneCount} scenes</p>
          )}
        </div>
      </div>

      {/* Info */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-sm font-medium text-gray-900">{template.name}</h3>
          {template.description && (
            <p className="mt-0.5 text-xs text-gray-500 line-clamp-2">{template.description}</p>
          )}
        </div>
        {template.is_system && <Lock className="h-3.5 w-3.5 text-gray-300 flex-shrink-0" />}
      </div>

      {/* Category badge */}
      {template.category && (
        <span className={`mt-2 inline-block rounded-full px-2 py-0.5 text-xs font-medium capitalize ${catColor}`}>
          {template.category}
        </span>
      )}

      {/* Actions */}
      <div className="mt-3 flex items-center gap-2">
        <button
          onClick={onUse}
          className="flex-1 rounded-lg bg-brand-50 py-1.5 text-xs font-medium text-brand-700 hover:bg-brand-100"
        >
          Use Template
        </button>
        <button
          onClick={onDuplicate}
          className="rounded-lg border border-gray-200 p-1.5 text-gray-400 hover:text-gray-600"
          title="Duplicate"
        >
          <Copy className="h-3.5 w-3.5" />
        </button>
        {onDelete && (
          <button
            onClick={onDelete}
            className="rounded-lg border border-gray-200 p-1.5 text-gray-400 hover:text-red-500"
            title="Delete"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    </div>
  )
}
