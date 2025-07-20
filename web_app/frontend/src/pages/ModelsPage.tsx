import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Cpu, Settings, RotateCcw, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

interface ModelConfig {
  model_name: string
  temperature: number
  max_tokens: number
  top_p: number
  verbose: boolean
}

interface Model {
  name: string
  available: boolean
  ollama_available: boolean
  transformers_available: boolean
}

export default function ModelsPage() {
  const [models, setModels] = useState<Model[]>([])
  const [loading, setLoading] = useState(true)
  const [restarting, setRestarting] = useState(false)
  
  const { register, handleSubmit, setValue, watch } = useForm<ModelConfig>()
  const temperature = watch('temperature')

  useEffect(() => {
    fetchModels()
  }, [])

  const fetchModels = async () => {
    try {
      const response = await fetch('/api/models')
      if (response.ok) {
        const data = await response.json()
        setModels(data)
        
        // Set default values
        if (data.length > 0) {
          setValue('model_name', data[0].name)
        }
      }
    } catch (error) {
      console.error('Error fetching models:', error)
      toast.error('Failed to load models')
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data: ModelConfig) => {
    try {
      const response = await fetch('/api/models/config', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      })

      if (response.ok) {
        toast.success('Model configuration updated successfully')
      } else {
        throw new Error('Failed to update model configuration')
      }
    } catch (error) {
      console.error('Error updating model config:', error)
      toast.error('Failed to update model configuration')
    }
  }

  const handleRestart = async () => {
    try {
      setRestarting(true)
      const response = await fetch('/api/models/restart', {
        method: 'POST',
      })

      if (response.ok) {
        toast.success('Model restarted successfully')
      } else {
        throw new Error('Failed to restart model')
      }
    } catch (error) {
      console.error('Error restarting model:', error)
      toast.error('Failed to restart model')
    } finally {
      setRestarting(false)
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Models</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Configure and manage AI model parameters
          </p>
        </div>
        <button
          onClick={handleRestart}
          disabled={restarting}
          className="btn-secondary flex items-center space-x-2 disabled:opacity-50"
        >
          {restarting ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
          ) : (
            <RotateCcw size={16} />
          )}
          <span>{restarting ? 'Restarting...' : 'Restart Model'}</span>
        </button>
      </div>

      {/* Available Models */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Available Models</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {models.map((model) => (
              <div
                key={model.name}
                className={`p-4 rounded-lg border ${
                  model.available
                    ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                    : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 dark:text-white">{model.name}</h4>
                  {model.available ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
                <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center space-x-2">
                    <Cpu size={14} />
                    <span>Ollama: {model.ollama_available ? 'Available' : 'Not Available'}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Settings size={14} />
                    <span>Transformers: {model.transformers_available ? 'Available' : 'Not Available'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Model Configuration */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Model Configuration</h3>
        </div>
        <div className="card-body">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Model Name
                </label>
                <select
                  {...register('model_name')}
                  className="input"
                >
                  {models.map((model) => (
                    <option key={model.name} value={model.name}>
                      {model.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Temperature
                </label>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    {...register('temperature', { valueAsNumber: true })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
                    <span>0.0 (Focused)</span>
                    <span className="font-medium">{temperature || 0.7}</span>
                    <span>2.0 (Creative)</span>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Max Tokens
                </label>
                <select
                  {...register('max_tokens', { valueAsNumber: true })}
                  className="input"
                >
                  <option value={512}>512 tokens</option>
                  <option value={1024}>1024 tokens</option>
                  <option value={2048}>2048 tokens</option>
                  <option value={4096}>4096 tokens</option>
                  <option value={8192}>8192 tokens</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Top P
                </label>
                <div className="space-y-2">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    {...register('top_p', { valueAsNumber: true })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
                    <span>0.0</span>
                    <span className="font-medium">{watch('top_p') || 0.9}</span>
                    <span>1.0</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Verbose Mode
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Enable detailed logging and debugging information
                </p>
              </div>
              <input
                type="checkbox"
                {...register('verbose')}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                className="btn-primary flex items-center space-x-2"
              >
                <Settings size={16} />
                <span>Update Configuration</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Model Information */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Model Information</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Temperature</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Controls randomness in the model's responses. Lower values make responses more focused and deterministic, while higher values increase creativity and variety.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Max Tokens</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                The maximum number of tokens the model will generate in a single response. Higher values allow for longer responses but may increase processing time.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Top P</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Controls diversity by considering only the most likely tokens whose cumulative probability exceeds the threshold. Lower values make responses more focused.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Verbose Mode</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                When enabled, provides detailed information about the model's thinking process, including chain of thought reasoning and daydreaming steps.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}