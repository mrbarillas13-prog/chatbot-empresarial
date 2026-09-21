import { useState, useRef, useEffect } from 'react'
import { renderMarkdown } from '../utils/markdown'
import { useLanguage } from '../contexts/LanguageContext'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface CartItem {
  id: string
  name: string
  price: number
  quantity: number
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const { t } = useLanguage()
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: t('chat.welcome') }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEnd = useRef<HTMLDivElement>(null)
  const sessionId = useRef(Math.random().toString(36).substring(2, 15))
  const cart = useRef<CartItem[]>([])

  useEffect(() => {
    const handler = (e: Event) => {
      const customEvent = e as CustomEvent
      const product = customEvent.detail
      if (product) {
        cart.current.push({
          id: product.id,
          name: product.name,
          price: product.price,
          quantity: product.quantity || 1
        })
        const cartMsg = `Quiero comprar ${product.name} por ${product.price} EUR`
        setIsOpen(true)
        setTimeout(() => {
          sendAutoMessage(cartMsg)
        }, 300)
      } else {
        setIsOpen(true)
      }
    }
    window.addEventListener('add-to-cart', handler)
    window.addEventListener('open-chatbot', handler)
    return () => {
      window.removeEventListener('add-to-cart', handler)
      window.removeEventListener('open-chatbot', handler)
    }
  }, [])

  useEffect(() => {
    messagesEnd.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendAutoMessage = async (text: string) => {
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId.current, message: text }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: t('chat.error') }])
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const text = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId.current, message: text }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: t('chat.error') }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isOpen && (
        <div className="mb-4 w-80 h-96 bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden">
          <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-cyan-400 rounded-full flex items-center justify-center text-blue-900 font-bold text-sm">T</div>
              <div>
                <div className="font-bold text-sm">TechStore Bot</div>
                <div className="text-xs text-cyan-300">Online agora</div>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-white/70 hover:text-white text-xl leading-none">&times;</button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, i) => (
              <div key={i} className={'flex ' + (msg.role === 'user' ? 'justify-end' : 'justify-start')}>
                <div className={
                  'max-w-[85%] px-3 py-2 rounded-2xl text-sm leading-relaxed ' +
                  (msg.role === 'user'
                    ? 'bg-blue-900 text-white rounded-br-md'
                    : 'bg-gray-100 text-gray-800 rounded-bl-md')
                }>
                  {renderMarkdown(msg.content)}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 px-4 py-3 rounded-2xl rounded-bl-md">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:'0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay:'.2s'}}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEnd} />
          </div>
          <div className="p-3 border-t border-gray-200">
            <div className="flex gap-2">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder={t('chat.placeholder')}
                className="flex-1 bg-gray-100 rounded-xl px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-900/30"
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || loading}
                className="bg-blue-900 text-white w-9 h-9 rounded-xl flex items-center justify-center hover:bg-blue-800 transition disabled:opacity-50"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </div>
          </div>
        </div>
      )}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={
          'w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 ' +
          (isOpen ? 'bg-gray-800 rotate-90' : 'bg-gradient-to-br from-blue-900 to-indigo-900 hover:scale-110')
        }
      >
        {isOpen ? (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        )}
      </button>
    </div>
  )
}
