import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { useThemeStore } from './stores/themeStore'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import AnalyticsPage from './pages/AnalyticsPage'
import SettingsPage from './pages/SettingsPage'
import ModelsPage from './pages/ModelsPage'
import TestsPage from './pages/TestsPage'
import ConversationsPage from './pages/ConversationsPage'

function App() {
  const { theme, initializeTheme } = useThemeStore()

  useEffect(() => {
    initializeTheme()
  }, [initializeTheme])

  useEffect(() => {
    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/models" element={<ModelsPage />} />
          <Route path="/tests" element={<TestsPage />} />
          <Route path="/conversations" element={<ConversationsPage />} />
        </Routes>
      </Layout>
    </div>
  )
}

export default App