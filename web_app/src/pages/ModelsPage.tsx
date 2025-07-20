import React, { useState, useEffect } from 'react'
import { Cpu, Play, Settings, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

interface ModelConfig {
  model_name: string
  temperature: number
  max_tokens: number
  verbose: boolean
}

interface ModelInfo {
  available_models: string[]
  current_model: string
  configuration: ModelConfig
}

const ModelsPage: React.FC = () => {
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null)
  const [config, setConfig] = useState<ModelConfig>({
    model_name: 'llama2',
    temperature: 0.7,
    max_tokens: 2048,
    verbose: false,
  })
  const [loading, setLoading] = useState(true)
  const [restarting, setRestarting] = useState(false)
  const [testing, setTesting] = useState(false)

  useEffect(() => {
    fetchModelInfo()
  }, [])

  const fetchModelInfo = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/models')
      if (response.ok) {
        const data = await response.json()
        setModelInfo(data)
        setConfig(data.configuration)
      }
    } catch (error) {
      console.error('Failed to fetch model info:', error)
      toast.error('Failed to load model information')
    } finally {
      setLoading(false)
    }
  }

  const restartModel = async () => {
    try {
      setRestarting(true)
      const response = await fetch('/api/models/restart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      })

      if (response.ok) {
        toast.success('Model restarted successfully')
        await fetchModelInfo() // Refresh model info
      } else {
        throw new Error('Failed to restart model')
      }
    } catch (error) {
      console.error('Failed to restart model:', error)
      toast.error('Failed to restart model')
    } finally {
      setRestarting(false)
    }
  }

  const testModel = async () => {
    try {
      setTesting(true)
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: 'Hello! This is a test message to verify the model is working correctly.',
          conversation_id: 'test',
        }),
      })

      if (response.ok) {
        const data = await response.json()
        toast.success('Model test successful!')
        console.log('Test response:', data)
      } else {
        throw new Error('Model test failed')
      }
    } catch (error) {
      console.error('Model test failed:', error)
      toast.error('Model test failed')
    } finally {
      setTesting(false)
    }
  }

  const handleConfigChange = (key: keyof ModelConfig, value: any) => {
    setConfig((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          AI Models
        </h1>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchModelInfo}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button
            onClick={testModel}
            disabled={testing}
            className="btn-secondary flex items-center space-x-2"
          >
            <Play className="w-4 h-4" />
            <span>{testing ? 'Testing...' : 'Test Model'}</span>
          </button>
          <button
            onClick={restartModel}
            disabled={restarting}
            className="btn-primary flex items-center space-x-2"
          >
            <Settings className="w-4 h-4" />
            <span>{restarting ? 'Restarting...' : 'Restart Model'}</span>
          </button>
        </div>
      </div>

      {/* Current Model Status */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Current Model Status
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-center space-x-3">
            <Cpu className="w-6 h-6 text-primary-600" />
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Active Model
              </p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {modelInfo?.current_model || 'None'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Status
              </p>
              <p className="text-lg font-semibold text-green-600">Active</p>
            </div>
          </div>
        </div>
      </div>

      {/* Model Configuration */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Model Configuration
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Model Name
            </label>
            <select
              value={config.model_name}
              onChange={(e) => handleConfigChange('model_name', e.target.value)}
              className="input-field"
            >
              {modelInfo?.available_models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Select the AI model to use
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Temperature
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.temperature}
              onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
            <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>0.0 (Deterministic)</span>
              <span>{config.temperature}</span>
              <span>2.0 (Very Random)</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max Tokens
            </label>
            <input
              type="number"
              value={config.max_tokens}
              onChange={(e) => handleConfigChange('max_tokens', parseInt(e.target.value))}
              min="100"
              max="8192"
              className="input-field"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Maximum number of tokens in response
            </p>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Verbose Mode
              </label>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Show detailed processing information
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={config.verbose}
                onChange={(e) => handleConfigChange('verbose', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Available Models */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Available Models
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modelInfo?.available_models.map((model) => (
            <div
              key={model}
              className={`p-4 rounded-lg border-2 ${
                model === modelInfo.current_model
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white">{model}</h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {model === modelInfo.current_model ? 'Active' : 'Available'}
                  </p>
                </div>
                {model === modelInfo.current_model && (
                  <CheckCircle className="w-5 h-5 text-primary-600" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Model Performance */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Model Performance
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              2.3s
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Average Response Time
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              99.2%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Success Rate
            </div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              1,247
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Total Requests
            </div>
          </div>
        </div>
      </div>

      {/* Model Information */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Model Information
        </h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-900 dark:text-white mb-2">
              Daydreamer AI Features
            </h4>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>True Chain of Thought reasoning</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>Creative day dreaming technique</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>Persistent memory across sessions</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>Clean Ollama integration</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ModelsPage