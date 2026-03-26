import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Share2, ExternalLink, Trash2, CheckCircle, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import { platformsApi } from '../api/platforms'
import type { PlatformAccount } from '../types/platform'

const PLATFORMS = [
  { id: 'youtube' as const, name: 'YouTube', color: 'bg-red-500', hoverColor: 'hover:bg-red-600' },
  { id: 'instagram' as const, name: 'Instagram', color: 'bg-pink-500', hoverColor: 'hover:bg-pink-600' },
  { id: 'twitter' as const, name: 'Twitter/X', color: 'bg-sky-500', hoverColor: 'hover:bg-sky-600' },
  { id: 'tiktok' as const, name: 'TikTok', color: 'bg-gray-900', hoverColor: 'hover:bg-gray-800' },
  { id: 'reddit' as const, name: 'Reddit', color: 'bg-orange-500', hoverColor: 'hover:bg-orange-600' },
]

export default function SocialAccounts() {
  const queryClient = useQueryClient()
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null)

  const { data: accounts = [], isLoading } = useQuery({
    queryKey: ['platform-accounts'],
    queryFn: () => platformsApi.list(),
    select: (res) => res.data,
  })

  const disconnectMutation = useMutation({
    mutationFn: (accountId: string) => platformsApi.disconnect(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['platform-accounts'] })
      toast.success('Account disconnected')
    },
    onError: () => toast.error('Failed to disconnect account'),
  })

  const handleConnect = async (platformId: string) => {
    setConnectingPlatform(platformId)
    try {
      const res = await platformsApi.getOAuthUrl(platformId)
      window.location.href = res.data.oauth_url
    } catch {
      toast.error(`Failed to get OAuth URL for ${platformId}`)
      setConnectingPlatform(null)
    }
  }

  const handleDisconnect = (account: PlatformAccount) => {
    if (window.confirm(`Disconnect ${account.display_name || account.platform}?`)) {
      disconnectMutation.mutate(account.id)
    }
  }

  const getConnectedAccounts = (platformId: string): PlatformAccount[] => {
    return accounts.filter((a) => a.platform === platformId && a.is_active)
  }

  // Check URL params for OAuth callback result
  const params = new URLSearchParams(window.location.search)
  const oauthSuccess = params.get('success')
  const oauthError = params.get('error')
  const oauthPlatform = params.get('platform')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Social Accounts</h1>
        <p className="text-sm text-gray-500">Connect your social media accounts for publishing</p>
      </div>

      {oauthSuccess && oauthPlatform && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-sm text-green-700">
          <CheckCircle className="mr-2 inline h-4 w-4" />
          Successfully connected your {oauthPlatform} account!
        </div>
      )}

      {oauthError && oauthPlatform && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to connect {oauthPlatform}: {oauthError}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {PLATFORMS.map((platform) => {
          const connected = getConnectedAccounts(platform.id)
          const isConnecting = connectingPlatform === platform.id

          return (
            <div
              key={platform.id}
              className="rounded-xl border border-gray-200 bg-white p-6"
            >
              <div className="flex items-center gap-3">
                <div className={`h-10 w-10 rounded-lg ${platform.color} flex items-center justify-center`}>
                  <Share2 className="h-5 w-5 text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{platform.name}</h3>
                  <p className="text-xs text-gray-500">
                    {connected.length > 0
                      ? `${connected.length} account${connected.length > 1 ? 's' : ''} connected`
                      : 'Not connected'}
                  </p>
                </div>
              </div>

              {connected.length > 0 && (
                <div className="mt-3 space-y-2">
                  {connected.map((account) => (
                    <div
                      key={account.id}
                      className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm"
                    >
                      <span className="text-gray-700 truncate">
                        {account.display_name || 'Connected'}
                      </span>
                      <button
                        onClick={() => handleDisconnect(account)}
                        disabled={disconnectMutation.isPending}
                        className="text-red-400 hover:text-red-600"
                        title="Disconnect"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <button
                onClick={() => handleConnect(platform.id)}
                disabled={isConnecting || isLoading}
                className={`mt-4 flex w-full items-center justify-center gap-2 rounded-lg py-2 text-sm font-medium ${
                  connected.length > 0
                    ? 'border border-gray-200 text-gray-600 hover:bg-gray-50'
                    : `${platform.color} ${platform.hoverColor} text-white`
                }`}
              >
                {isConnecting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Connecting...
                  </>
                ) : (
                  <>
                    <ExternalLink className="h-4 w-4" />
                    {connected.length > 0 ? 'Add Another Account' : 'Connect'}
                  </>
                )}
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
