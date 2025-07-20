import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: string
  thinkingTime?: number
  daydreamTime?: number
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
}

interface ChatState {
  conversations: Conversation[]
  currentConversationId: string | null
  isLoading: boolean
  error: string | null
  
  // Actions
  createConversation: (title?: string) => string
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => void
  setCurrentConversation: (conversationId: string) => void
  deleteConversation: (conversationId: string) => void
  clearConversations: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  getCurrentConversation: () => Conversation | null
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      conversations: [],
      currentConversationId: null,
      isLoading: false,
      error: null,

      createConversation: (title = 'New Conversation') => {
        const id = crypto.randomUUID()
        const now = new Date().toISOString()
        const conversation: Conversation = {
          id,
          title,
          messages: [],
          createdAt: now,
          updatedAt: now,
        }
        
        set((state) => ({
          conversations: [conversation, ...state.conversations],
          currentConversationId: id,
        }))
        
        return id
      },

      addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => {
        const newMessage: Message = {
          ...message,
          id: crypto.randomUUID(),
          timestamp: new Date().toISOString(),
        }

        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  messages: [...conv.messages, newMessage],
                  updatedAt: new Date().toISOString(),
                  title: conv.messages.length === 0 ? message.content.slice(0, 50) + '...' : conv.title,
                }
              : conv
          ),
        }))
      },

      setCurrentConversation: (conversationId: string) => {
        set({ currentConversationId: conversationId })
      },

      deleteConversation: (conversationId: string) => {
        set((state) => {
          const newConversations = state.conversations.filter((conv) => conv.id !== conversationId)
          const newCurrentId = state.currentConversationId === conversationId
            ? (newConversations[0]?.id || null)
            : state.currentConversationId

          return {
            conversations: newConversations,
            currentConversationId: newCurrentId,
          }
        })
      },

      clearConversations: () => {
        set({ conversations: [], currentConversationId: null })
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      },

      setError: (error: string | null) => {
        set({ error })
      },

      getCurrentConversation: () => {
        const { conversations, currentConversationId } = get()
        return conversations.find((conv) => conv.id === currentConversationId) || null
      },
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({
        conversations: state.conversations,
        currentConversationId: state.currentConversationId,
      }),
    }
  )
)