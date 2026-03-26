import { useVideoStore } from '../../stores/videoStore'

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'tr', name: 'Turkish' },
  { code: 'de', name: 'German' },
  { code: 'fr', name: 'French' },
  { code: 'es', name: 'Spanish' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'zh', name: 'Chinese' },
  { code: 'ar', name: 'Arabic' },
  { code: 'pt', name: 'Portuguese' },
  { code: 'ru', name: 'Russian' },
  { code: 'it', name: 'Italian' },
]

export default function LanguageSelector() {
  const { languages, setLanguages } = useVideoStore()

  const toggleLanguage = (code: string) => {
    if (languages.includes(code)) {
      if (languages.length > 1) {
        setLanguages(languages.filter((l) => l !== code))
      }
    } else {
      setLanguages([...languages, code])
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Languages</label>
      <div className="flex flex-wrap gap-2">
        {LANGUAGES.map((lang) => (
          <button
            key={lang.code}
            onClick={() => toggleLanguage(lang.code)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
              languages.includes(lang.code)
                ? 'bg-brand-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {lang.name}
          </button>
        ))}
      </div>
      <p className="text-xs text-gray-500">
        Multiple languages will generate separate video variants with translated content.
      </p>
    </div>
  )
}
