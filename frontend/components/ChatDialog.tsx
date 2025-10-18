'use client'

import { useEffect, useRef, useState } from 'react'
import { supabase } from '@/lib/client'
import { Send, X } from 'lucide-react'

type Message = {
  role: 'user' | 'bot'
  content: string
}

interface ChatDialogProps {
  isOpen: boolean
  onClose: () => void
}

export default function ChatDialog({ isOpen, onClose }: ChatDialogProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Auto-scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  useEffect(() => {
    // Focus input when dialog opens
    if (isOpen) {
      inputRef.current?.focus()
    }
  }, [isOpen])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = input.trim()
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setInput('')
    setLoading(true)

    try {
      // Get user
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) {
        setMessages(prev => [...prev, { role: 'bot', content: 'Please log in to use the chat.' }])
        setLoading(false)
        return
      }

      // Call API
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, message: userMessage })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()

      // Add bot response
      setMessages(prev => [...prev, { role: 'bot', content: data.response }])
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const starterPrompts = [
    "What food groups am I missing today?",
    "What should I eat for more protein?",
    "Review my meals from today"
  ]

  const handlePromptClick = (prompt: string) => {
    setInput(prompt)
    inputRef.current?.focus()
  }

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
      />
      
      {/* Dialog - Bottom Right */}
      <div className="fixed bottom-6 right-6 w-[28rem] h-[700px] bg-white rounded-2xl shadow-2xl z-50 flex flex-col border border-[#D9F1E3]">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#D9F1E3]">
          <h2 className="text-lg font-bold text-[#0B3B29]">NutriBalance Assistant</h2>
          <button
            onClick={onClose}
            className="text-[#5E7F73] hover:text-[#0B3B29] transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && (
            <div className="text-center space-y-4 mt-8">
              <div className="space-y-1">
                <h3 className="text-base font-semibold text-[#0B3B29]">
                  Hi! I'm your nutrition assistant.
                </h3>
                <p className="text-sm text-[#5E7F73]">
                  Ask me about your diet and nutrition.
                </p>
              </div>
              
              <div className="space-y-2">
                <p className="text-xs font-semibold text-[#5E7F73]">Try asking:</p>
                <div className="flex flex-col gap-2">
                  {starterPrompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handlePromptClick(prompt)}
                      className="px-3 py-2 bg-[#F1FBF6] text-[#2BAA66] rounded-lg text-xs hover:bg-[#D9F1E3] transition-all text-left"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-3 py-2 rounded-lg text-sm ${
                  msg.role === 'user'
                    ? 'bg-[#2BAA66] text-white'
                    : 'bg-gray-50 text-[#0B3B29]'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-50 px-3 py-2 rounded-lg">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-[#D9F1E3]">
          <div className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              disabled={loading}
              className="flex-1 border border-[#D9F1E3] rounded-lg px-3 py-2 text-sm outline-none focus:border-[#2BAA66] disabled:bg-gray-50 disabled:cursor-not-allowed"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-[#2BAA66] text-white p-2 rounded-lg hover:bg-[#27A05F] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

