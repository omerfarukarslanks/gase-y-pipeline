import { Sparkles } from 'lucide-react'
import { useVideoStore } from '../../stores/videoStore'

export default function PromptInput() {
  const { prompt, setPrompt } = useVideoStore()

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Video Prompt
      </label>
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe the video you want to create... e.g., 'Create a 30-second educational video about climate change with engaging visuals and narration'"
          className="w-full rounded-xl border border-gray-300 px-4 py-3 pr-12 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200 min-h-[120px] resize-y"
        />
        <Sparkles className="absolute right-3 top-3 h-5 w-5 text-brand-400" />
      </div>
      <p className="text-xs text-gray-500">
        Be as detailed as possible. Include tone, style, target audience, and key points.
      </p>
    </div>
  )
}
