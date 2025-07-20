import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Save, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { useThemeStore } from '../stores/themeStore'

interface Settings {
  theme: string
  language: string
  auto_save: boolean
  notifications_enabled: boolean
  max_conversation_history: number
}

export default function SettingsPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const { theme, setTheme } = useThemeStore()
  
  const { register, handleSubmit, setValue, watch } = useForm<Settings>()
  const notificationsEnabled = watch('notifications_enabled')

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/settings')
      if (response.ok) {
        const settings = await response.json()
        setValue('theme', settings.theme)
        setValue('language', settings.language)
        setValue('auto_save', settings.auto_save)
        setValue('notifications_enabled', settings.notifications_enabled)
        setValue('max_conversation_history', settings.max_conversation_history)
      }
    } catch (error) {
      console.error('Error fetching settings:', error)
      toast.error('Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data: Settings) => {
    try {
      setSaving(true)
      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (response.ok) {
        toast.success('Settings saved successfully')
        // Update theme if changed
        if (data.theme !== theme) {
          setTheme(data.theme as 'light' | 'dark')
        }
      } else {
        throw new Error('Failed to save settings')
      }
    } catch (error) {
      console.error('Error saving settings:', error)
      toast.error('Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Configure your Daydreamer experience
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Appearance */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Appearance</h3>
          </div>
          <div className="card-body space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Theme
              </label>
              <select
                {...register('theme')}
                className="input"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="auto">Auto (System)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Language
              </label>
              <select
                {...register('language')}
                className="input"
              >
                <option value="en">English</option>
                <option value="es">Español</option>
                <option value="fr">Français</option>
                <option value="de">Deutsch</option>
                <option value="it">Italiano</option>
                <option value="pt">Português</option>
              </select>
            </div>
          </div>
        </div>

        {/* Behavior */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Behavior</h3>
          </div>
          <div className="card-body space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Auto-save conversations
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Automatically save conversations to your history
                </p>
              </div>
              <input
                type="checkbox"
                {...register('auto_save')}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Enable notifications
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Receive notifications for important events
                </p>
              </div>
              <input
                type="checkbox"
                {...register('notifications_enabled')}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Max conversation history
              </label>
              <select
                {...register('max_conversation_history')}
                className="input"
              >
                <option value={50}>50 conversations</option>
                <option value={100}>100 conversations</option>
                <option value={200}>200 conversations</option>
                <option value={500}>500 conversations</option>
                <option value={1000}>1000 conversations</option>
              </select>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Maximum number of conversations to keep in history
              </p>
            </div>
          </div>
        </div>

        {/* Notifications Settings */}
        {notificationsEnabled && (
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Notifications</h3>
            </div>
            <div className="card-body space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Model status updates
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Notify when AI model status changes
                  </p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Test completion alerts
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Notify when automated tests complete
                  </p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    System health warnings
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Notify when system resources are low
                  </p>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={fetchSettings}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw size={16} />
            <span>Reset</span>
          </button>
          <button
            type="submit"
            disabled={saving}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50"
          >
            {saving ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Save size={16} />
            )}
            <span>{saving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>
      </form>
    </div>
  )
}