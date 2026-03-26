import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Star, Trash2, Copy, Clock, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { promptsApi } from '../api/platforms'
import { useVideoStore } from '../stores/videoStore'
import type { PromptHistoryEntry } from '../types/platform'

export default function PromptHistory() {
  const [tab, setTab] = useState<'all' | 'favorites'>('all')
  const [page, setPage] = useState(1)
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const setPrompt = useVideoStore((s) => s.setPrompt)

  const { data: history = [], isLoading: historyLoading } = useQuery({
    queryKey: ['prompt-history', page],
    queryFn: () => promptsApi.history(page),
    select: (res) => res.data,
  })

  const { data: favorites = [], isLoading: favoritesLoading } = useQuery({
    queryKey: ['prompt-favorites'],
    queryFn: () => promptsApi.favorites(),
    select: (res) => res.data,
  })

  const toggleFavorite = useMutation({
    mutationFn: (id: string) => promptsApi.toggleFavorite(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompt-history'] })
      queryClient.invalidateQueries({ queryKey: ['prompt-favorites'] })
    },
  })

  const deletePrompt = useMutation({
    mutationFn: (id: string) => promptsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompt-history'] })
      queryClient.invalidateQueries({ queryKey: ['prompt-favorites'] })
      toast.success('Prompt deleted')
    },
  })

  const handleUsePrompt = (entry: PromptHistoryEntry) => {
    setPrompt(entry.prompt_text)
    navigate('/create')
    toast.success('Prompt loaded')
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
  }

  const items = tab === 'all' ? history : favorites
  const isLoading = tab === 'all' ? historyLoading : favoritesLoading

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Prompt History</h1>
        <p className="text-sm text-gray-500">Your previous prompts and favorites</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-gray-100 p-1">
        <button
          onClick={() => setTab('all')}
          className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === 'all'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Clock className="mr-1.5 inline h-4 w-4" />
          All History
        </button>
        <button
          onClick={() => setTab('favorites')}
          className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
            tab === 'favorites'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Star className="mr-1.5 inline h-4 w-4" />
          Favorites ({favorites.length})
        </button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      ) : items.length === 0 ? (
        <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
          <p className="text-gray-500">
            {tab === 'all'
              ? 'No prompts yet. Create a video to start building your history.'
              : 'No favorites yet. Star a prompt to save it here.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((entry) => (
            <div
              key={entry.id}
              className="group rounded-xl border border-gray-200 bg-white p-4 transition-shadow hover:shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <p
                  className="flex-1 cursor-pointer text-sm text-gray-800 hover:text-brand-600"
                  onClick={() => handleUsePrompt(entry)}
                  title="Click to use this prompt"
                >
                  {entry.prompt_text}
                </p>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => toggleFavorite.mutate(entry.id)}
                    className={`rounded p-1 transition-colors ${
                      entry.is_favorite
                        ? 'text-yellow-500 hover:text-yellow-600'
                        : 'text-gray-300 hover:text-yellow-500'
                    }`}
                    title={entry.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    <Star className="h-4 w-4" fill={entry.is_favorite ? 'currentColor' : 'none'} />
                  </button>
                  <button
                    onClick={() => handleCopy(entry.prompt_text)}
                    className="rounded p-1 text-gray-300 transition-colors hover:text-gray-600"
                    title="Copy"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => deletePrompt.mutate(entry.id)}
                    className="rounded p-1 text-gray-300 transition-colors hover:text-red-500"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
                <span>{new Date(entry.created_at).toLocaleDateString()}</span>
                {entry.project_id && (
                  <span
                    className="cursor-pointer text-brand-500 hover:underline"
                    onClick={() => navigate(`/videos/${entry.project_id}`)}
                  >
                    View project
                  </span>
                )}
              </div>
            </div>
          ))}

          {/* Pagination for history tab */}
          {tab === 'all' && items.length >= 20 && (
            <div className="flex justify-center gap-2 pt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="rounded-lg border border-gray-200 px-4 py-2 text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                className="rounded-lg border border-gray-200 px-4 py-2 text-sm"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
