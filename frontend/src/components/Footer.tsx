import { useLanguage } from '../contexts/LanguageContext'

export default function Footer() {
  const { t } = useLanguage()

  return (
    <footer id="contato" className="bg-gray-900 text-white py-12 px-6 lg:px-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-cyan-400 rounded-lg flex items-center justify-center font-bold text-blue-900">T</div>
            <span className="text-lg font-bold">TechStore</span>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed">
            {t('footer.desc')}
          </p>
        </div>
        <div>
          <h4 className="font-bold mb-4">{t('footer.links')}</h4>
          <ul className="space-y-2 text-gray-400 text-sm">
            <li><a href="#productos" className="hover:text-cyan-400 transition">{t('footer.products')}</a></li>
            <li><a href="#contato" className="hover:text-cyan-400 transition">{t('footer.contact')}</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold mb-4">{t('footer.support')}</h4>
          <p className="text-gray-400 text-sm">{t('footer.support_desc')}</p>
          <p className="text-gray-400 text-sm mt-2">{t('footer.email')}</p>
        </div>
      </div>
      <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
        {t('footer.copyright')}
      </div>
    </footer>
  )
}
