interface HeaderProps {
  onToggleSidebar: () => void
  onNewChat: () => void
  username: string | null
  onLogout: () => void
  onGoLanding?: () => void
}

export default function Header({ onToggleSidebar, onNewChat, username, onLogout, onGoLanding }: HeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button onClick={onToggleSidebar} className="lg:hidden p-2 hover:bg-gray-100 rounded-lg">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-900 rounded-lg flex items-center justify-center text-white font-bold text-sm">T</div>
          <span className="font-bold text-gray-900">TechStore</span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        {onGoLanding && (
          <button onClick={onGoLanding} className="text-sm text-gray-600 hover:text-blue-900 transition font-medium">
            Catalogo
          </button>
        )}
        <button onClick={onNewChat} className="bg-blue-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-800 transition">
          + Novo Chat
        </button>
        <span className="text-sm text-gray-500 hidden sm:block">{username}</span>
        <button onClick={onLogout} className="text-sm text-red-600 hover:text-red-800 transition font-medium">
          Sair
        </button>
      </div>
    </header>
  )
}
