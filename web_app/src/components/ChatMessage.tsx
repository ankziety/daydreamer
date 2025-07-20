import React from 'react'
import { Message } from '../stores/chatStore'
import { User, Bot, Clock, Zap } from 'lucide-react'

interface ChatMessageProps {
  message: Message
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user'
  const timestamp = new Date(message.timestamp).toLocaleTimeString()

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`flex max-w-3xl ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}
      >
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser
              ? 'bg-primary-600 text-white ml-3'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 mr-3'
          }`}
        >
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
        </div>

        {/* Message content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div
            className={`inline-block px-4 py-2 rounded-lg ${
              isUser
                ? 'bg-primary-600 text-white'
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100'
            }`}
          >
            <div className="whitespace-pre-wrap">{message.content}</div>
          </div>

          {/* Message metadata */}
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-2">
              <Clock className="w-3 h-3" />
              <span>{timestamp}</span>
            </div>

            {!isUser && (message.thinkingTime || message.daydreamTime) && (
              <div className="flex items-center space-x-2">
                {message.thinkingTime && (
                  <div className="flex items-center space-x-1">
                    <Zap className="w-3 h-3" />
                    <span>Think: {message.thinkingTime.toFixed(1)}s</span>
                  </div>
                )}
                {message.daydreamTime && (
                  <div className="flex items-center space-x-1">
                    <Zap className="w-3 h-3" />
                    <span>Dream: {message.daydreamTime.toFixed(1)}s</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatMessage