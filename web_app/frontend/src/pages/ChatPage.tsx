import { useState, useRef, useEffect } from 'react'
import { Send, Loader2, Trash2, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'
import ChatMessage from '../components/ChatMessage'
import { useChatStore } from '../stores/chatStore'

export default function ChatPage() {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const { 
    messages, 
    conversationId, 
    addMessage, 
    clearMessages, 
    restartConversation,
    loadConversation 
  } = useChatStore()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
      thinkingTime: 0,
      daydreamTime: 0
    })

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_id: conversationId
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      
      // Add AI response
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        thinkingTime: data.thinking_time || 0,
        daydreamTime: data.daydream_time || 0
      })

      // Update conversation ID if it's a new conversation
      if (data.conversation_id && data.conversation_id !== conversationId) {
        // This would update the conversation ID in the store
      }

    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to send message. Please try again.')
      
      // Add error message
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        thinkingTime: 0,
        daydreamTime: 0,
        isError: true
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    if (messages.length > 0) {
      clearMessages()
      toast.success('Conversation cleared')
    }
  }

  const handleRestart = () => {
    restartConversation()
    toast.success('Conversation restarted')
  }

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Chat with Daydreamer</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Experience true chain of thought reasoning and creative daydreaming
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleRestart}
            className="btn-secondary flex items-center space-x-2"
            title="Restart conversation"
          >
            <RotateCcw size={16} />
            <span>Restart</span>
          </button>
          <button
            onClick={handleClear}
            className="btn-danger flex items-center space-x-2"
            title="Clear conversation"
          >
            <Trash2 size={16} />
            <span>Clear</span>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 dark:text-gray-500 mb-4">
              <Send size={48} className="mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Start a conversation
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Ask me anything and experience the power of daydreaming AI
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))
        )}
        
        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
            <Loader2 size={16} className="animate-spin" />
            <span>Daydreamer is thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex space-x-4">
        <div className="flex-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="input"
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Send size={16} />
          )}
          <span>Send</span>
        </button>
      </form>
    </div>
  )
}