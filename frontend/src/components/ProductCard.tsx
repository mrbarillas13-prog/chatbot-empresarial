import { useLanguage } from '../contexts/LanguageContext'

interface ProductProps {
  product: {
    id: string
    name: string
    name_pt?: string
    description?: string
    description_pt?: string
    price: number
    category: string
    stock: number
    image_url?: string
  }
}

const categoryIcons: Record<string, string> = {
  Laptops: '\uD83D\uDCBB',
  Accesorios: '\uD83C\uDFA7',
}

const categoryColors: Record<string, string> = {
  Laptops: 'from-blue-500 to-indigo-600',
  Accesorios: 'from-emerald-500 to-teal-600',
}

export default function ProductCard({ product }: ProductProps) {
  const { lang, t } = useLanguage()
  const displayName = lang === 'pt' ? (product.name_pt || product.name) : product.name
  const displayDesc = lang === 'pt' ? (product.description_pt || product.description || '') : (product.description || '')
  const icon = categoryIcons[product.category] || '\uD83D\uDCE6'
  const gradient = categoryColors[product.category] || 'from-gray-500 to-gray-600'

  let stockText = t('card.in_stock')
  let stockColor = 'text-green-600'
  if (product.stock === 0) {
    stockText = t('card.out_of_stock')
    stockColor = 'text-red-600'
  } else if (product.stock <= 10) {
    stockText = t('card.low_stock') + ' ' + product.stock + ' ' + t('card.stock_remaining')
    stockColor = 'text-amber-600'
  }

  const handleAddToCart = () => {
    window.dispatchEvent(new CustomEvent('add-to-cart', {
      detail: {
        id: product.id,
        name: displayName,
        price: product.price,
        quantity: 1
      }
    }))
  }

  return (
    <div className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group border border-gray-100">
      <div className={'h-32 bg-gradient-to-br ' + gradient + ' flex items-center justify-center'}>
        <span className="text-5xl group-hover:scale-110 transition-transform duration-300">{icon}</span>
      </div>
      <div className="p-5">
        <div className="flex items-start justify-between mb-2">
          <h4 className="font-bold text-gray-900 text-base leading-tight flex-1">{displayName}</h4>
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full ml-2 whitespace-nowrap">{product.category}</span>
        </div>
        <p className="text-gray-500 text-sm mb-3 line-clamp-2 leading-relaxed">{displayDesc}</p>
        <div className="flex items-end justify-between">
          <div>
            <span className="text-2xl font-extrabold text-blue-900">{product.price.toFixed(2)} &euro;</span>
          </div>
          <span className={'text-xs font-medium ' + stockColor}>{stockText}</span>
        </div>
        <button
          onClick={handleAddToCart}
          className="w-full mt-4 bg-blue-900 text-white py-2.5 rounded-xl font-semibold hover:bg-blue-800 transition text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={product.stock === 0}
        >
          {product.stock === 0 ? t('card.unavailable') : t('card.add_cart')}
        </button>
      </div>
    </div>
  )
}
