import { useLanguage } from '../contexts/LanguageContext'

export default function Hero() {
  const { lang, setLang, t } = useLanguage()

  const openChat = () => {
    window.dispatchEvent(new CustomEvent('open-chatbot'))
  }

  return (
    <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white overflow-hidden">
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-400 rounded-full blur-3xl"></div>
        <div className="absolute bottom-10 right-20 w-96 h-96 bg-purple-400 rounded-full blur-3xl"></div>
      </div>
      <nav className="relative z-10 flex items-center justify-between px-6 lg:px-12 py-4">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-cyan-400 rounded-lg flex items-center justify-center font-bold text-blue-900 text-xl">T</div>
          <span className="text-xl font-bold tracking-tight">TechStore</span>
        </div>
        <div className="hidden md:flex items-center gap-6 text-sm font-medium">
          <a href="#productos" className="hover:text-cyan-300 transition">{t('hero.nav_products')}</a>
          <a href="#contato" className="hover:text-cyan-300 transition">{t('hero.nav_contact')}</a>
          <div className="flex items-center gap-1 bg-white/10 rounded-lg px-1 py-0.5">
            {(['es', 'pt', 'en'] as const).map(l => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={'px-2 py-1 rounded text-xs font-bold transition ' + (lang === l ? 'bg-cyan-400 text-blue-900' : 'text-white/70 hover:text-white')}
              >
                {l.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <a href="#productos" className="bg-cyan-400 text-blue-900 px-5 py-2 rounded-lg font-semibold hover:bg-cyan-300 transition text-sm">
            {t('hero.nav_catalog')}
          </a>
          <div className="flex md:hidden items-center gap-1 bg-white/10 rounded-lg px-1 py-0.5">
            {(['es', 'pt', 'en'] as const).map(l => (
              <button
                key={l}
                onClick={() => setLang(l)}
                className={'px-2 py-1 rounded text-xs font-bold transition ' + (lang === l ? 'bg-cyan-400 text-blue-900' : 'text-white/70 hover:text-white')}
              >
                {l.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </nav>
      <div className="relative z-10 max-w-6xl mx-auto px-6 lg:px-12 py-20 lg:py-32">
        <div className="max-w-2xl">
          <div className="inline-block bg-cyan-400/20 text-cyan-300 px-4 py-1 rounded-full text-sm font-medium mb-6">
            {t('hero.badge')}
          </div>
          <h1 className="text-4xl lg:text-6xl font-extrabold leading-tight mb-6">
            {t('hero.title1')} <span className="text-cyan-400">{t('hero.title2')}</span> {t('hero.title3')}
          </h1>
          <p className="text-lg text-blue-200 mb-8 leading-relaxed">
            {t('hero.desc')}
          </p>
          <div className="flex flex-wrap gap-4">
            <a href="#productos" className="bg-cyan-400 text-blue-900 px-8 py-3 rounded-lg font-bold hover:bg-cyan-300 transition text-lg">
              {t('hero.btn_products')}
            </a>
            <button onClick={openChat} className="border-2 border-white/30 text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition text-lg">
              {t('hero.btn_chat')}
            </button>
          </div>
          <div className="flex gap-12 mt-12 text-center">
            <div>
              <div className="text-3xl font-extrabold text-cyan-400">33+</div>
              <div className="text-sm text-blue-300">{t('hero.stat_products')}</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold text-cyan-400">24h</div>
              <div className="text-sm text-blue-300">{t('hero.stat_support')}</div>
            </div>
            <div>
              <div className="text-3xl font-extrabold text-cyan-400">3</div>
              <div className="text-sm text-blue-300">{t('hero.stat_languages')}</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
