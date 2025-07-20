import React, { useState, useRef, useEffect } from 'react'
import { Send, Plus, Trash2, RotateCcw } from 'lucide-react'
import { useChatStore } from '../stores/chatStore'
import ChatMessage from '../components/ChatMessage'
import toast from 'react-hot-toast'

const ChatPage: React.FC = () => {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const {
    conversations,
    currentConversationId,
    createConversation,
    addMessage,
    getCurrentConversation,
    clearConversations,
    setLoading,
  } = useChatStore()

  const currentConversation = getCurrentConversation()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentConversation?.messages])

  // Auto-focus input when conversation changes
  useEffect(() => {
    inputRef.current?.focus()
  }, [currentConversationId])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const message = input.trim()
    setInput('')
    setIsLoading(true)
    setLoading(true)

    // Create conversation if none exists
    const conversationId = currentConversationId || createConversation()

    // Add user message
    addMessage(conversationId, {
      content: message,
      role: 'user',
    })

    try {
      // Send to API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()

      // Add AI response
      addMessage(conversationId, {
        content: data.response,
        role: 'assistant',
        thinkingTime: data.thinking_time,
        daydreamTime: data.daydream_time,
      })

      toast.success('Message sent successfully')
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message')
      
      // Add error message
      addMessage(conversationId, {
        content: 'Sorry, I encountered an error while processing your message. Please try again.',
        role: 'assistant',
      })
    } finally {
      setIsLoading(false)
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleNewConversation = () => {
    createConversation()
    toast.success('New conversation started')
  }

  const handleClearConversations = () => {
    if (window.confirm('Are you sure you want to clear all conversations? This action cannot be undone.')) {
      clearConversations()
      toast.success('All conversations cleared')
    }
  }

  const handleClearContext = () => {
    if (currentConversationId) {
      // Create a new conversation to clear context
      createConversation()
      toast.success('Context cleared')
    }
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Chat with Daydreamer AI
        </h1>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleNewConversation}
            className="btn-secondary flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
          <button
            onClick={handleClearContext}
            className="btn-secondary flex items-center space-x-2"
            title="Clear current conversation context"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Clear Context</span>
          </button>
          <button
            onClick={handleClearConversations}
            className="btn-danger flex items-center space-x-2"
            title="Clear all conversations"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear All</span>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        {currentConversation?.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <div className="text-center">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-lg font-medium mb-2">Welcome to Daydreamer AI</h3>
              <p className="text-sm">
                Start a conversation to experience true chain of thought reasoning and creative day dreaming.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {currentConversation?.messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                  <div className="animate-pulse-slow">🤔</div>
                  <span className="text-sm">Daydreamer is thinking...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex items-end space-x-2">
        <div className="flex-1">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here... (Shift+Enter for new line)"
            className="input-field resize-none"
            rows={3}
            disabled={isLoading}
          />
        </div>
        <button
          onClick={handleSendMessage}
          disabled={!input.trim() || isLoading}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </div>

      {/* Conversation info */}
      {currentConversation && (
        <div className="mt-4 text-sm text-gray-500 dark:text-gray-400">
          <p>
            Conversation: {currentConversation.title} •{' '}
            {currentConversation.messages.length} messages •{' '}
            Last updated: {new Date(currentConversation.updatedAt).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  )
}

export default ChatPage