import { useState, useRef, useEffect } from 'react'
import { renderMarkdown } from '../utils/markdown'

interface Message {
  role: 'user' | 'assistant'
  content: string
  action?: string
  timestamp: Date
}

interface ChatProps {
  messages: Message[]
  onSend: (msg: string) => void
  loading: boolean
}

export default function Chat({ messages, onSend, loading }: ChatProps) {
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = () => {
    if (!input.trim() || loading) return
    onSend(input.trim())
    setInput('')
  }

  const quickActions = [
    { label: 'Ver productos', icon: '📦', msg: 'Que productos tienen?' },
    { label: 'Consultar stock', icon: '📊', msg: 'Que productos tienen stock disponible?' },
    { label: 'Soporte', icon: '🎧', msg: 'Necesito ayuda con soporte' },
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 animate-fade-in">
            <div className="text-6xl mb-4">💬</div>
            <h2 className="text-xl font-semibold text-gray-600 mb-2">Bienvenido a TechStore</h2>
            <p className="text-sm text-center max-w-md">Escribe un mensaje o usa los botones de accion rapida para empezar.</p>
            <div className="flex gap-2 mt-6">
              {quickActions.map((a) => (
                <button
                  key={a.label}
                  onClick={() => onSend(a.msg)}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-700 hover:bg-brand-50 hover:border-brand-300 hover:text-brand-700 transition-all shadow-sm"
                >
                  <span>{a.icon}</span>
                  {a.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-sm font-bold mr-2 mt-1 flex-shrink-0">
                T
              </div>
            )}
            <div className={`max-w-[75%] ${msg.role === 'user' ? 'order-1' : ''}`}>
              <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-brand-500 text-white rounded-br-md'
                  : 'bg-white text-gray-800 border border-gray-100 shadow-sm rounded-bl-md'
              }`}>
                {renderMarkdown(msg.content)}
              </div>
              <div className={`text-xs text-gray-400 mt-1 ${msg.role === 'user' ? 'text-right' : 'text-left'} px-1`}>
                {msg.timestamp.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' })}
                {msg.action && msg.role === 'assistant' && (
                  <span className="ml-2 px-1.5 py-0.5 bg-gray-100 rounded text-gray-500">{msg.action}</span>
                )}
              </div>
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-white text-sm font-bold ml-2 mt-1 flex-shrink-0">
                U
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start animate-slide-up">
            <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-sm font-bold mr-2 flex-shrink-0">
              T
            </div>
            <div className="px-4 py-3 bg-white border border-gray-100 shadow-sm rounded-2xl rounded-bl-md">
              <div className="flex gap-1">
                <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full inline-block"></span>
                <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full inline-block"></span>
                <span className="typing-dot w-2 h-2 bg-gray-400 rounded-full inline-block"></span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Quick actions bar */}
      {messages.length > 0 && messages.length < 4 && (
        <div className="px-4 pb-2 flex gap-2 overflow-x-auto">
          {quickActions.map((a) => (
            <button
              key={a.label}
              onClick={() => onSend(a.msg)}
              className="flex items-center gap-1 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-xs text-gray-600 hover:bg-brand-50 hover:border-brand-300 transition-all whitespace-nowrap"
            >
              <span>{a.icon}</span>
              {a.label}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-100 bg-white">
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Escribe tu mensaje..."
            disabled={loading}
            className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition-all disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-5 py-3 bg-brand-500 text-white rounded-xl text-sm font-medium hover:bg-brand-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

