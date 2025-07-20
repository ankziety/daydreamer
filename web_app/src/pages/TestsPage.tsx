import React, { useState, useEffect } from 'react'
import { TestTube, Play, Clock, CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

interface TestResult {
  id: number
  test_name: string
  status: 'passed' | 'failed' | 'error'
  duration: number
  timestamp: string
  details: Record<string, any>
  error_message?: string
}

interface TestSuite {
  name: string
  description: string
  tests: string[]
}

const TestsPage: React.FC = () => {
  const [testResults, setTestResults] = useState<TestResult[]>([])
  const [runningTests, setRunningTests] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [statistics, setStatistics] = useState({
    total_tests: 0,
    passed_tests: 0,
    failed_tests: 0,
    error_tests: 0,
    success_rate: 0,
  })

  const testSuites: TestSuite[] = [
    {
      name: 'API Tests',
      description: 'Test API endpoints and responses',
      tests: ['test_chat_endpoint', 'test_models_endpoint', 'test_analytics_endpoint'],
    },
    {
      name: 'Model Tests',
      description: 'Test AI model functionality',
      tests: ['test_model_initialization', 'test_model_response', 'test_model_config'],
    },
    {
      name: 'Database Tests',
      description: 'Test database operations',
      tests: ['test_conversation_save', 'test_settings_save', 'test_metrics_save'],
    },
    {
      name: 'Integration Tests',
      description: 'Test system integration',
      tests: ['test_full_conversation_flow', 'test_websocket_connection', 'test_error_handling'],
    },
  ]

  useEffect(() => {
    fetchTestResults()
  }, [])

  const fetchTestResults = async () => {
    try {
      setLoading(true)
      // Mock API call - replace with actual endpoint
      const mockResults: TestResult[] = [
        {
          id: 1,
          test_name: 'test_chat_endpoint',
          status: 'passed',
          duration: 1.2,
          timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
          details: { response_time: 1200, status_code: 200 },
        },
        {
          id: 2,
          test_name: 'test_model_initialization',
          status: 'passed',
          duration: 0.8,
          timestamp: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
          details: { model_loaded: true, memory_allocated: '512MB' },
        },
        {
          id: 3,
          test_name: 'test_database_connection',
          status: 'failed',
          duration: 2.1,
          timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
          details: { connection_timeout: true },
          error_message: 'Database connection timeout after 2 seconds',
        },
        {
          id: 4,
          test_name: 'test_websocket_connection',
          status: 'error',
          duration: 0.5,
          timestamp: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
          details: { websocket_error: true },
          error_message: 'WebSocket connection failed',
        },
      ]

      setTestResults(mockResults)
      calculateStatistics(mockResults)
    } catch (error) {
      console.error('Failed to fetch test results:', error)
      toast.error('Failed to load test results')
    } finally {
      setLoading(false)
    }
  }

  const calculateStatistics = (results: TestResult[]) => {
    const total = results.length
    const passed = results.filter((r) => r.status === 'passed').length
    const failed = results.filter((r) => r.status === 'failed').length
    const error = results.filter((r) => r.status === 'error').length
    const successRate = total > 0 ? (passed / total) * 100 : 0

    setStatistics({
      total_tests: total,
      passed_tests: passed,
      failed_tests: failed,
      error_tests: error,
      success_rate: successRate,
    })
  }

  const runTest = async (testName: string) => {
    try {
      setRunningTests((prev) => [...prev, testName])
      
      // Mock test execution - replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 2000 + Math.random() * 3000))
      
      const success = Math.random() > 0.2 // 80% success rate
      const status = success ? 'passed' : Math.random() > 0.5 ? 'failed' : 'error'
      
      const newResult: TestResult = {
        id: Date.now(),
        test_name: testName,
        status,
        duration: 1.5 + Math.random() * 2,
        timestamp: new Date().toISOString(),
        details: { mock_test: true },
        error_message: !success ? 'Test failed due to mock error' : undefined,
      }

      setTestResults((prev) => [newResult, ...prev])
      calculateStatistics([newResult, ...testResults])
      
      toast.success(`Test ${testName} ${status}`)
    } catch (error) {
      console.error(`Test ${testName} failed:`, error)
      toast.error(`Test ${testName} failed`)
    } finally {
      setRunningTests((prev) => prev.filter((t) => t !== testName))
    }
  }

  const runTestSuite = async (suite: TestSuite) => {
    try {
      toast.loading(`Running ${suite.name} tests...`)
      
      for (const test of suite.tests) {
        await runTest(test)
      }
      
      toast.success(`${suite.name} test suite completed`)
    } catch (error) {
      console.error(`${suite.name} test suite failed:`, error)
      toast.error(`${suite.name} test suite failed`)
    }
  }

  const runAllTests = async () => {
    try {
      toast.loading('Running all tests...')
      
      for (const suite of testSuites) {
        for (const test of suite.tests) {
          await runTest(test)
        }
      }
      
      toast.success('All tests completed')
    } catch (error) {
      console.error('All tests failed:', error)
      toast.error('All tests failed')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />
      default:
        return <Clock className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20'
      case 'failed':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20'
      case 'error':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20'
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Automated Tests
        </h1>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchTestResults}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <button
            onClick={runAllTests}
            className="btn-primary flex items-center space-x-2"
          >
            <Play className="w-4 h-4" />
            <span>Run All Tests</span>
          </button>
        </div>
      </div>

      {/* Test Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="card text-center">
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {statistics.total_tests}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Total Tests</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600">
            {statistics.passed_tests}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Passed</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-red-600">
            {statistics.failed_tests}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Failed</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-yellow-600">
            {statistics.error_tests}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Errors</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-blue-600">
            {statistics.success_rate.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Success Rate</div>
        </div>
      </div>

      {/* Test Suites */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {testSuites.map((suite) => (
          <div key={suite.name} className="card">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {suite.name}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {suite.description}
                </p>
              </div>
              <button
                onClick={() => runTestSuite(suite)}
                className="btn-secondary flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Run Suite</span>
              </button>
            </div>
            <div className="space-y-2">
              {suite.tests.map((test) => (
                <div
                  key={test}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    {runningTests.includes(test) ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                    ) : (
                      getStatusIcon(
                        testResults.find((r) => r.test_name === test)?.status || 'pending'
                      )
                    )}
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {test}
                    </span>
                  </div>
                  <button
                    onClick={() => runTest(test)}
                    disabled={runningTests.includes(test)}
                    className="btn-secondary text-xs disabled:opacity-50"
                  >
                    {runningTests.includes(test) ? 'Running...' : 'Run'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Recent Test Results */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Recent Test Results
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Test Name
                </th>
                <th className="text-left py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Status
                </th>
                <th className="text-left py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Duration
                </th>
                <th className="text-left py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Timestamp
                </th>
                <th className="text-left py-2 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">
                  Details
                </th>
              </tr>
            </thead>
            <tbody>
              {testResults.slice(0, 10).map((result) => (
                <tr
                  key={result.id}
                  className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(result.status)}
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {result.test_name}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                        result.status
                      )}`}
                    >
                      {result.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                    {result.duration.toFixed(2)}s
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                    {new Date(result.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    {result.error_message && (
                      <div className="text-xs text-red-600 dark:text-red-400 max-w-xs truncate">
                        {result.error_message}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default TestsPage