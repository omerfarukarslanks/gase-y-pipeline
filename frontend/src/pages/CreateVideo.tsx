import { useState } from 'react'
import { Wand2 } from 'lucide-react'
import { toast } from 'sonner'
import PromptInput from '../components/video/PromptInput'
import LanguageSelector from '../components/video/LanguageSelector'
import PlatformSelector from '../components/video/PlatformSelector'
import VideoEditor from '../components/video/VideoEditor'
import { useVideoStore } from '../stores/videoStore'
import { useCreateProject, useGenerateVideo } from '../hooks/useVideo'

export default function CreateVideo() {
  const [step, setStep] = useState<'prompt' | 'settings' | 'generating'>('prompt')
  const store = useVideoStore()
  const createProject = useCreateProject()
  const generateVideo = useGenerateVideo()

  const handleGenerate = async () => {
    if (!store.prompt.trim()) {
      toast.error('Please enter a prompt')
      return
    }

    try {
      const project = await createProject.mutateAsync({
        title: store.prompt.slice(0, 100),
        prompt: store.prompt,
        settings: {
          ai_provider: store.aiProvider,
          tts_provider: store.ttsProvider,
          languages: store.languages,
          platforms: store.selectedPlatforms,
        },
      })

      await generateVideo.mutateAsync({
        project_id: project.data.id,
        languages: store.languages,
        aspect_ratio: store.aspectRatio,
        resolution: '1080p',
        ai_provider: store.aiProvider,
        tts_provider: store.ttsProvider,
      })

      setStep('generating')
    } catch {
      // Error already handled by mutation hooks
    }
  }

  const isLoading = createProject.isPending || generateVideo.isPending

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Create Video</h1>
        <p className="text-sm text-gray-500">
          Enter a prompt and configure your video settings
        </p>
      </div>

      {step === 'generating' ? (
        <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
          <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-brand-600" />
          <h3 className="mt-6 text-lg font-medium text-gray-900">Generating your video...</h3>
          <p className="mt-2 text-sm text-gray-500">
            This may take a few minutes. We'll notify you when it's ready.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <PromptInput />
          </div>

          {step === 'prompt' && store.prompt.trim() && (
            <button
              onClick={() => setStep('settings')}
              className="w-full rounded-lg border border-brand-200 bg-brand-50 py-3 text-sm font-medium text-brand-700 hover:bg-brand-100"
            >
              Continue to Settings
            </button>
          )}

          {step === 'settings' && (
            <>
              <div className="rounded-xl border border-gray-200 bg-white p-6 space-y-6">
                <VideoEditor />
                <LanguageSelector />
                <PlatformSelector />
              </div>

              <button
                onClick={handleGenerate}
                disabled={isLoading}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 py-3 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
              >
                <Wand2 className="h-4 w-4" />
                {isLoading ? 'Starting...' : 'Generate Video'}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}
