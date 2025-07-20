import { useState, useEffect } from 'react'
import { TestTube, Play, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

interface Test {
  id: string
  name: string
  description: string
  parameters: Record<string, any>
}

interface TestResult {
  id: number
  test_name: string
  test_type: string
  status: 'passed' | 'failed' | 'error'
  duration: number
  parameters: Record<string, any>
  results: Record<string, any>
  error_message?: string
  created_at: string
}

export default function TestsPage() {
  const [tests, setTests] = useState<Test[]>([])
  const [results, setResults] = useState<TestResult[]>([])
  const [loading, setLoading] = useState(true)
  const [runningTest, setRunningTest] = useState<string | null>(null)

  useEffect(() => {
    fetchTests()
    fetchResults()
  }, [])

  const fetchTests = async () => {
    try {
      const response = await fetch('/api/tests')
      if (response.ok) {
        const data = await response.json()
        setTests(data)
      }
    } catch (error) {
      console.error('Error fetching tests:', error)
      toast.error('Failed to load tests')
    }
  }

  const fetchResults = async () => {
    try {
      const response = await fetch('/api/tests/results')
      if (response.ok) {
        const data = await response.json()
        setResults(data)
      }
    } catch (error) {
      console.error('Error fetching results:', error)
      toast.error('Failed to load test results')
    } finally {
      setLoading(false)
    }
  }

  const runTest = async (testType: string) => {
    try {
      setRunningTest(testType)
      const response = await fetch('/api/tests/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_type: testType,
          parameters: {}
        }),
      })

      if (response.ok) {
        const result = await response.json()
        toast.success(`${result.test_name} completed successfully`)
        fetchResults() // Refresh results
      } else {
        throw new Error('Failed to run test')
      }
    } catch (error) {
      console.error('Error running test:', error)
      toast.error('Failed to run test')
    } finally {
      setRunningTest(null)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      default:
        return <Clock className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'status-success'
      case 'failed':
        return 'status-error'
      case 'error':
        return 'status-warning'
      default:
        return 'status-info'
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
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Automated Tests</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Run automated tests to verify system functionality and performance
        </p>
      </div>

      {/* Available Tests */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Available Tests</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tests.map((test) => (
              <div
                key={test.id}
                className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <TestTube className="h-5 w-5 text-primary-500" />
                    <h4 className="font-medium text-gray-900 dark:text-white">{test.name}</h4>
                  </div>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {test.description}
                </p>
                <button
                  onClick={() => runTest(test.id)}
                  disabled={runningTest === test.id}
                  className="btn-primary w-full flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {runningTest === test.id ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  ) : (
                    <Play size={16} />
                  )}
                  <span>
                    {runningTest === test.id ? 'Running...' : 'Run Test'}
                  </span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Test Results */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Test Results</h3>
        </div>
        <div className="card-body">
          {results.length === 0 ? (
            <div className="text-center py-8">
              <TestTube className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">No test results yet</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Test
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                  {results.map((result) => (
                    <tr key={result.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {result.test_name}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            {result.test_type}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(result.status)}
                          <span className={`status-indicator ${getStatusColor(result.status)}`}>
                            {result.status}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {result.duration.toFixed(2)}s
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {format(new Date(result.created_at), 'MMM dd, HH:mm')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Test Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {results.filter(r => r.status === 'passed').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Passed Tests</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {results.filter(r => r.status === 'failed').length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Failed Tests</div>
          </div>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {results.length > 0 
                ? (results.filter(r => r.status === 'passed').length / results.length * 100).toFixed(1)
                : 0
              }%
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Success Rate</div>
          </div>
        </div>
      </div>
    </div>
  )
}