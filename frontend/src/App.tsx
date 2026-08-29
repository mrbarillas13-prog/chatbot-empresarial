import { useState, useCallback } from 'react'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Chat from './components/Chat'

const API_URL = ''

interface Message {
  role: 'user' | 'assistant'
  content: string
  action?: string
  timestamp: Date
}

interface Conversation {
  id: string
  title: string
  lastMessage: string
  timestamp: Date
  messageCount: number
}

function App() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConvId, setActiveConvId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const generateId = () => Math.random().toString(36).substring(2, 15)

  const createNewChat = useCallback(() => {
    const newId = generateId()
    const newConv: Conversation = {
      id: newId,
      title: 'Nueva conversacion',
      lastMessage: '',
      timestamp: new Date(),
      messageCount: 0,
    }
    setConversations(prev => [newConv, ...prev])
    setActiveConvId(newId)
    setMessages([])
    setSidebarOpen(false)
  }, [])

  const sendMessage = useCallback(async (text: string) => {
    const sessionId = activeConvId || generateId()

    if (!activeConvId) {
      const newConv: Conversation = {
        id: sessionId,
        title: text.length > 30 ? text.substring(0, 30) + '...' : text,
        lastMessage: text,
        timestamp: new Date(),
        messageCount: 1,
      }
      setConversations(prev => [newConv, ...prev])
      setActiveConvId(sessionId)
    }

    const userMsg: Message = { role: 'user', content: text, timestamp: new Date() }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      })
      const data = await res.json()

      const assistantMsg: Message = {
        role: 'assistant',
        content: data.reply,
        action: data.action,
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, assistantMsg])

      setConversations(prev =>
        prev.map(c =>
          c.id === sessionId
            ? { ...c, lastMessage: data.reply.substring(0, 50), timestamp: new Date(), messageCount: c.messageCount + 2 }
            : c
        )
      )
    } catch {
      const errorMsg: Message = {
        role: 'assistant',
        content: 'Error al conectar con el backend. Verifica que el servidor este corriendo.',
        timestamp: new Date(),
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }, [activeConvId])

  const selectConversation = useCallback((id: string) => {
    setActiveConvId(id)
    setMessages([])
    setSidebarOpen(false)
  }, [])

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={createNewChat}
      />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          conversations={conversations}
          activeId={activeConvId}
          onSelect={selectConversation}
          onNew={createNewChat}
          isOpen={sidebarOpen}
          onToggle={() => setSidebarOpen(!sidebarOpen)}
        />
        <main className="flex-1 flex flex-col overflow-hidden">
          <Chat
            messages={messages}
            onSend={sendMessage}
            loading={loading}
          />
        </main>
      </div>
    </div>
  )
}

export default App

