import { format } from 'date-fns'
import { User, Bot, Clock, Zap } from 'lucide-react'
import { Message } from '../stores/chatStore'

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'
  const totalTime = message.thinkingTime + message.daydreamTime

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-3xl ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-primary-500 text-white' 
            : 'bg-gray-500 text-white'
        }`}>
          {isUser ? <User size={16} /> : <Bot size={16} />}
        </div>

        {/* Message content */}
        <div className={`flex-1 ${isUser ? 'text-right' : 'text-left'}`}>
          <div className={`inline-block px-4 py-2 rounded-lg ${
            isUser
              ? 'bg-primary-500 text-white'
              : message.isError
              ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
              : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
          }`}>
            <div className="whitespace-pre-wrap">{message.content}</div>
          </div>

          {/* Message metadata */}
          <div className={`flex items-center space-x-2 mt-2 text-xs text-gray-500 dark:text-gray-400 ${
            isUser ? 'justify-end' : 'justify-start'
          }`}>
            <div className="flex items-center space-x-1">
              <Clock size={12} />
              <span>{format(message.timestamp, 'HH:mm')}</span>
            </div>
            
            {!isUser && totalTime > 0 && (
              <div className="flex items-center space-x-1">
                <Zap size={12} />
                <span>{totalTime.toFixed(1)}s</span>
                {message.thinkingTime > 0 && (
                  <span className="text-blue-500">(think: {message.thinkingTime.toFixed(1)}s)</span>
                )}
                {message.daydreamTime > 0 && (
                  <span className="text-purple-500">(dream: {message.daydreamTime.toFixed(1)}s)</span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}