import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  thinkingTime: number
  daydreamTime: number
  isError?: boolean
}

interface ChatState {
  messages: Message[]
  conversationId: string | null
  addMessage: (message: Message) => void
  clearMessages: () => void
  restartConversation: () => void
  loadConversation: (conversationId: string) => void
  setConversationId: (id: string | null) => void
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      conversationId: null,
      
      addMessage: (message: Message) => {
        set((state) => ({
          messages: [...state.messages, message]
        }))
      },
      
      clearMessages: () => {
        set({
          messages: [],
          conversationId: null
        })
      },
      
      restartConversation: () => {
        set({
          messages: [],
          conversationId: null
        })
      },
      
      loadConversation: async (conversationId: string) => {
        try {
          const response = await fetch(`/api/conversations/${conversationId}`)
          if (response.ok) {
            const data = await response.json()
            const messages: Message[] = data.messages.map((msg: any) => ({
              id: msg.id.toString(),
              role: msg.role,
              content: msg.content,
              timestamp: new Date(msg.timestamp),
              thinkingTime: msg.thinking_time,
              daydreamTime: msg.daydream_time
            }))
            
            set({
              messages,
              conversationId
            })
          }
        } catch (error) {
          console.error('Error loading conversation:', error)
        }
      },
      
      setConversationId: (id: string | null) => {
        set({ conversationId: id })
      }
    }),
    {
      name: 'chat-store',
      partialize: (state) => ({
        messages: state.messages.slice(-50), // Only persist last 50 messages
        conversationId: state.conversationId
      })
    }
  )
)