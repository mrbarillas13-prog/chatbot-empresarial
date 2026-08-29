interface Product {
  id: string
  name: string
  description: string
  price: number
  category: string
  stock: number
}

interface ProductCardProps {
  product: Product
}

export default function ProductCard({ product }: ProductCardProps) {
  const stockColor = product.stock > 20 ? 'text-green-600 bg-green-50' : product.stock > 0 ? 'text-yellow-600 bg-yellow-50' : 'text-red-600 bg-red-50'
  const stockText = product.stock > 20 ? 'En stock' : product.stock > 0 ? `Solo ${product.stock}` : 'Agotado'

  const categoryColors: Record<string, string> = {
    'Electronica': 'bg-blue-100 text-blue-700',
    'Accesorios': 'bg-purple-100 text-purple-700',
    'Audio': 'bg-pink-100 text-pink-700',
    'Almacenamiento': 'bg-green-100 text-green-700',
    'Mobiliario': 'bg-orange-100 text-orange-700',
  }

  const catColor = categoryColors[product.category] || 'bg-gray-100 text-gray-700'

  return (
    <div className="bg-white border border-gray-100 rounded-xl p-3 shadow-sm hover:shadow-md transition-shadow max-w-xs">
      <div className="flex items-start justify-between mb-2">
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${catColor}`}>
          {product.category}
        </span>
        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${stockColor}`}>
          {stockText}
        </span>
      </div>
      <h4 className="font-semibold text-gray-800 text-sm mb-1">{product.name}</h4>
      <p className="text-xs text-gray-500 mb-2 line-clamp-2">{product.description}</p>
      <div className="flex items-center justify-between">
        <span className="text-lg font-bold text-brand-600">${product.price.toFixed(2)}</span>
        <span className="text-xs text-gray-400">Stock: {product.stock}</span>
      </div>
    </div>
  )
}
