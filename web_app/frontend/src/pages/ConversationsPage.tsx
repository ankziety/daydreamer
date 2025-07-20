import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { History, MessageSquare, Clock, Trash2, Eye } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  total_thinking_time: number
  total_daydream_time: number
  tags: string[]
}

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState<string | null>(null)

  useEffect(() => {
    fetchConversations()
  }, [])

  const fetchConversations = async () => {
    try {
      const response = await fetch('/api/conversations')
      if (response.ok) {
        const data = await response.json()
        setConversations(data)
      }
    } catch (error) {
      console.error('Error fetching conversations:', error)
      toast.error('Failed to load conversations')
    } finally {
      setLoading(false)
    }
  }

  const deleteConversation = async (id: string) => {
    try {
      setDeleting(id)
      const response = await fetch(`/api/conversations/${id}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        toast.success('Conversation deleted')
        setConversations(conversations.filter(c => c.id !== id))
      } else {
        throw new Error('Failed to delete conversation')
      }
    } catch (error) {
      console.error('Error deleting conversation:', error)
      toast.error('Failed to delete conversation')
    } finally {
      setDeleting(null)
    }
  }

  const clearAllConversations = async () => {
    if (!confirm('Are you sure you want to delete all conversations? This action cannot be undone.')) {
      return
    }

    try {
      const response = await fetch('/api/conversations/clear', {
        method: 'POST',
      })

      if (response.ok) {
        toast.success('All conversations cleared')
        setConversations([])
      } else {
        throw new Error('Failed to clear conversations')
      }
    } catch (error) {
      console.error('Error clearing conversations:', error)
      toast.error('Failed to clear conversations')
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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Conversation History</h1>
          <p className="text-gray-600 dark:text-gray-400">
            View and manage your past conversations with Daydreamer
          </p>
        </div>
        {conversations.length > 0 && (
          <button
            onClick={clearAllConversations}
            className="btn-danger flex items-center space-x-2"
          >
            <Trash2 size={16} />
            <span>Clear All</span>
          </button>
        )}
      </div>

      {/* Conversations List */}
      {conversations.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-12">
            <History className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No conversations yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Start a conversation to see your history here
            </p>
            <Link
              to="/chat"
              className="btn-primary inline-flex items-center space-x-2"
            >
              <MessageSquare size={16} />
              <span>Start Chatting</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="card-body">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-medium text-gray-900 dark:text-white line-clamp-2">
                    {conversation.title || 'Untitled Conversation'}
                  </h3>
                  <button
                    onClick={() => deleteConversation(conversation.id)}
                    disabled={deleting === conversation.id}
                    className="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-50"
                  >
                    {deleting === conversation.id ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                    ) : (
                      <Trash2 size={16} />
                    )}
                  </button>
                </div>

                <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <div className="flex items-center space-x-2">
                    <MessageSquare size={14} />
                    <span>{conversation.message_count} messages</span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Clock size={14} />
                    <span>
                      {format(new Date(conversation.updated_at), 'MMM dd, HH:mm')}
                    </span>
                  </div>

                  {(conversation.total_thinking_time > 0 || conversation.total_daydream_time > 0) && (
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span>
                        Think: {conversation.total_thinking_time.toFixed(1)}s, 
                        Dream: {conversation.total_daydream_time.toFixed(1)}s
                      </span>
                    </div>
                  )}
                </div>

                {conversation.tags.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {conversation.tags.slice(0, 3).map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
                      >
                        {tag}
                      </span>
                    ))}
                    {conversation.tags.length > 3 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                        +{conversation.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}

                <div className="mt-4 flex space-x-2">
                  <Link
                    to={`/chat?conversation=${conversation.id}`}
                    className="btn-primary flex-1 flex items-center justify-center space-x-2"
                  >
                    <Eye size={16} />
                    <span>View</span>
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Statistics */}
      {conversations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {conversations.length}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Conversations</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                {conversations.reduce((sum, c) => sum + c.message_count, 0)}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Messages</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                {conversations.reduce((sum, c) => sum + c.total_thinking_time, 0).toFixed(1)}s
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Thinking Time</div>
            </div>
          </div>
          <div className="card">
            <div className="card-body text-center">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                {conversations.reduce((sum, c) => sum + c.total_daydream_time, 0).toFixed(1)}s
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Daydream Time</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}