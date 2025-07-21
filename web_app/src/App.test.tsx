import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from './App'

// Mock the stores to avoid issues with localStorage
vi.mock('./stores/themeStore', () => ({
  useThemeStore: () => ({
    theme: 'dark',
    toggleTheme: vi.fn(),
    setTheme: vi.fn(),
  }),
}))

vi.mock('./stores/chatStore', () => ({
  useChatStore: () => ({
    messages: [],
    addMessage: vi.fn(),
    clearMessages: vi.fn(),
    conversations: [],
    addConversation: vi.fn(),
    deleteConversation: vi.fn(),
    clearConversations: vi.fn(),
  }),
}))

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    // Check that the app renders without throwing errors
    expect(document.body).toBeInTheDocument()
  })

  it('has main app container', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    // The app should have a main container
    const appContainer = document.querySelector('#root')
    expect(appContainer).toBeInTheDocument()
  })
})