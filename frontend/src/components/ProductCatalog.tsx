import { useState, useEffect } from 'react'
import ProductCard from './ProductCard'
import { useLanguage } from '../contexts/LanguageContext'

interface Product {
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

export default function ProductCatalog() {
  const [products, setProducts] = useState<Product[]>([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const { t } = useLanguage()

  useEffect(() => {
    fetch('/api/catalog')
      .then(r => r.json())
      .then(data => {
        setProducts(Array.isArray(data) ? data : [])
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const filtered = filter === 'all' ? products : products.filter(p => p.category === filter)
  const laptops = filtered.filter(p => p.category === 'Laptops')
  const accesorios = filtered.filter(p => p.category === 'Accesorios')

  return (
    <section id="productos" className="py-16 px-6 lg:px-12 max-w-7xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-3xl lg:text-4xl font-extrabold text-gray-900 mb-4">{t('catalog.title')}</h2>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          {t('catalog.desc')}
        </p>
      </div>
      <div className="flex justify-center gap-3 mb-10 flex-wrap">
        {[
          ['all', t('catalog.filter_all')],
          ['Laptops', t('catalog.filter_laptops')],
          ['Accesorios', t('catalog.filter_accessories')]
        ].map(([cat, label]) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={
              'px-6 py-2 rounded-full font-medium transition ' +
              (filter === cat
                ? 'bg-blue-900 text-white shadow-lg'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300')
            }
          >
            {label}
          </button>
        ))}
      </div>
      {loading ? (
        <div className="text-center py-20 text-gray-500">{t('catalog.loading')}</div>
      ) : (
        <>
          {laptops.length > 0 && (
            <div className="mb-12">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <span className="w-2 h-2 bg-blue-600 rounded-full"></span>
                {t('catalog.section_laptops')}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {laptops.map(p => <ProductCard key={p.id} product={p} />)}
              </div>
            </div>
          )}
          {accesorios.length > 0 && (
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-600 rounded-full"></span>
                {t('catalog.section_accessories')}
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {accesorios.map(p => <ProductCard key={p.id} product={p} />)}
              </div>
            </div>
          )}
        </>
      )}
    </section>
  )
}
