import React, { useState, useEffect } from 'react'
import { History, Search, Trash2, Eye, Calendar, MessageSquare, Clock } from 'lucide-react'
import { useChatStore, Conversation } from '../stores/chatStore'
import toast from 'react-hot-toast'

const ConversationsPage: React.FC = () => {
  const { conversations, setCurrentConversation, deleteConversation, clearConversations } = useChatStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedConversation, setSelectedConversation] = useState<Conversation | null>(null)
  const [filter, setFilter] = useState<'all' | 'recent' | 'favorites'>('all')

  const filteredConversations = conversations.filter((conv) => {
    const matchesSearch = conv.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      conv.messages.some(msg => msg.content.toLowerCase().includes(searchTerm.toLowerCase()))
    
    if (filter === 'recent') {
      const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      return matchesSearch && new Date(conv.updatedAt) > oneWeekAgo
    }
    
    return matchesSearch
  })

  const handleViewConversation = (conversation: Conversation) => {
    setSelectedConversation(conversation)
    setCurrentConversation(conversation.id)
  }

  const handleDeleteConversation = (conversationId: string) => {
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      deleteConversation(conversationId)
      if (selectedConversation?.id === conversationId) {
        setSelectedConversation(null)
      }
      toast.success('Conversation deleted')
    }
  }

  const handleClearAll = () => {
    if (window.confirm('Are you sure you want to clear all conversations? This action cannot be undone.')) {
      clearConversations()
      setSelectedConversation(null)
      toast.success('All conversations cleared')
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)
    
    if (diffInHours < 1) {
      return 'Just now'
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)} hours ago`
    } else if (diffInHours < 168) { // 7 days
      return `${Math.floor(diffInHours / 24)} days ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const getConversationPreview = (conversation: Conversation) => {
    const lastMessage = conversation.messages[conversation.messages.length - 1]
    if (lastMessage) {
      return lastMessage.content.length > 100 
        ? lastMessage.content.substring(0, 100) + '...'
        : lastMessage.content
    }
    return 'No messages yet'
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Conversation History
        </h1>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleClearAll}
            className="btn-danger flex items-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear All</span>
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as 'all' | 'recent' | 'favorites')}
            className="input-field"
          >
            <option value="all">All Conversations</option>
            <option value="recent">Recent (7 days)</option>
            <option value="favorites">Favorites</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Conversation List */}
        <div className="lg:col-span-1">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Conversations ({filteredConversations.length})
            </h3>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {filteredConversations.length === 0 ? (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <History className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No conversations found</p>
                </div>
              ) : (
                filteredConversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedConversation?.id === conversation.id
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }`}
                    onClick={() => handleViewConversation(conversation)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 dark:text-white truncate">
                          {conversation.title}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                          {getConversationPreview(conversation)}
                        </p>
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                          <div className="flex items-center space-x-1">
                            <MessageSquare className="w-3 h-3" />
                            <span>{conversation.messages.length}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{formatDate(conversation.updatedAt)}</span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteConversation(conversation.id)
                        }}
                        className="ml-2 p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Conversation Detail */}
        <div className="lg:col-span-2">
          {selectedConversation ? (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {selectedConversation.title}
                  </h3>
                  <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500 dark:text-gray-400">
                    <div className="flex items-center space-x-1">
                      <MessageSquare className="w-4 h-4" />
                      <span>{selectedConversation.messages.length} messages</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>Created {formatDate(selectedConversation.createdAt)}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-4 h-4" />
                      <span>Updated {formatDate(selectedConversation.updatedAt)}</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setCurrentConversation(selectedConversation.id)}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Eye className="w-4 h-4" />
                  <span>Open in Chat</span>
                </button>
              </div>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {selectedConversation.messages.map((message, index) => (
                  <div
                    key={message.id}
                    className={`p-4 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-primary-100 dark:bg-primary-900/20 ml-8'
                        : 'bg-gray-100 dark:bg-gray-800 mr-8'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                          message.role === 'user'
                            ? 'bg-primary-600'
                            : 'bg-gray-600'
                        }`}
                      >
                        {message.role === 'user' ? 'U' : 'AI'}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-900 dark:text-white">
                            {message.role === 'user' ? 'You' : 'Daydreamer AI'}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                          {message.content}
                        </div>
                        {message.thinkingTime && message.daydreamTime && (
                          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                            <span>Think: {message.thinkingTime.toFixed(1)}s</span>
                            <span>Dream: {message.daydreamTime.toFixed(1)}s</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="card">
              <div className="text-center py-12">
                <History className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No Conversation Selected
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Select a conversation from the list to view its details
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Statistics */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Conversation Statistics
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {conversations.length}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Conversations</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {conversations.reduce((total, conv) => total + conv.messages.length, 0)}
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Total Messages</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {conversations.length > 0 
                ? Math.round(conversations.reduce((total, conv) => total + conv.messages.length, 0) / conversations.length)
                : 0
              }
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Avg Messages/Conv</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {conversations.length > 0 
                ? formatDate(conversations[0].updatedAt)
                : 'N/A'
              }
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Last Activity</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConversationsPage