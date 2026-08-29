interface QuickAction {
  icon: string
  label: string
  msg: string
  color: string
}

interface QuickActionsProps {
  onSelect: (msg: string) => void
}

const actions: QuickAction[] = [
  { icon: '📦', label: 'Ver catalogo', msg: 'Que productos tienen?', color: 'bg-blue-50 hover:bg-blue-100 border-blue-200 text-blue-700' },
  { icon: '🔍', label: 'Buscar producto', msg: 'Busco un producto especifico', color: 'bg-purple-50 hover:bg-purple-100 border-purple-200 text-purple-700' },
  { icon: '📊', label: 'Consultar stock', msg: 'Que productos tienen stock disponible?', color: 'bg-green-50 hover:bg-green-100 border-green-200 text-green-700' },
  { icon: '🎧', label: 'Soporte', msg: 'Necesito ayuda con soporte', color: 'bg-orange-50 hover:bg-orange-100 border-orange-200 text-orange-700' },
  { icon: '🛒', label: 'Mis pedidos', msg: 'Quiero ver el estado de mi pedido', color: 'bg-pink-50 hover:bg-pink-100 border-pink-200 text-pink-700' },
]

export default function QuickActions({ onSelect }: QuickActionsProps) {
  return (
    <div className="flex flex-wrap gap-2 justify-center">
      {actions.map((a) => (
        <button
          key={a.label}
          onClick={() => onSelect(a.msg)}
          className={`flex items-center gap-2 px-4 py-2.5 border rounded-xl text-sm font-medium transition-all shadow-sm hover:shadow ${a.color}`}
        >
          <span className="text-lg">{a.icon}</span>
          {a.label}
        </button>
      ))}
    </div>
  )
}
