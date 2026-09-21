import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

type Lang = 'es' | 'pt' | 'en'

interface LanguageContextType {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: string) => string
}

const translations: Record<Lang, Record<string, string>> = {
  es: {
    // Hero
    'hero.badge': 'Tecnologia de ultima generacion',
    'hero.title1': 'Encuentra el',
    'hero.title2': 'notebook perfecto',
    'hero.title3': 'para ti',
    'hero.desc': 'Laptops gaming, profesionales y para el dia a dia. Accesorios completos, precios competitivos y asistencia tecnica especializada.',
    'hero.btn_products': 'Explorar Productos',
    'hero.btn_chat': 'Habla con nuestro Chatbot',
    'hero.stat_products': 'Productos',
    'hero.stat_support': 'Soporte',
    'hero.stat_languages': 'Idiomas',
    'hero.nav_products': 'Productos',
    'hero.nav_contact': 'Contacto',
    'hero.nav_catalog': 'Ver Catalogo',
    // ProductCatalog
    'catalog.title': 'Nuestros Productos',
    'catalog.desc': 'Explora nuestro catalogo completo de notebooks y accesorios',
    'catalog.filter_all': 'Todos',
    'catalog.filter_laptops': 'Notebooks',
    'catalog.filter_accessories': 'Accesorios',
    'catalog.loading': 'Cargando productos...',
    'catalog.section_laptops': 'Notebooks',
    'catalog.section_accessories': 'Accesorios',
    // ProductCard
    'card.add_cart': 'Agregar al Carrito',
    'card.unavailable': 'No Disponible',
    'card.in_stock': 'En stock',
    'card.low_stock': 'Solo quedan',
    'card.out_of_stock': 'Agotado',
    'card.stock_remaining': 'disponibles',
    // Footer
    'footer.desc': 'Tu tienda de tecnologia con los mejores notebooks y accesorios del mercado.',
    'footer.links': 'Enlaces',
    'footer.products': 'Productos',
    'footer.contact': 'Contacto',
    'footer.support': 'Soporte',
    'footer.support_desc': 'Chatbot disponible 24/7 en Portugues, Espanol e Ingles.',
    'footer.email': 'Email: soporte@techstore.com',
    'footer.copyright': '2026 TechStore. Todos los derechos reservados. Proyecto portfolio chatbot-as-a-service.',
    // ChatWidget
    'chat.welcome': 'Hola! Soy el asistente de TechStore. Como puedo ayudarte?',
    'chat.placeholder': 'Escribe tu mensaje...',
    'chat.error': 'Error al conectar. Intenta de nuevo.',
    // App
    'app.admin_panel': 'Panel Admin',
    'app.logout': 'Salir',
    'app.logged_in': 'Conectado como',
  },
  pt: {
    'hero.badge': 'Tecnologia de ultima geracao',
    'hero.title1': 'Encontre a',
    'hero.title2': 'notebook perfeita',
    'hero.title3': 'para voce',
    'hero.desc': 'Laptops gaming, profissionais e para o dia a dia. Acessorios completos, precos competitivos e assistencia tecnica especializada.',
    'hero.btn_products': 'Explorar Produtos',
    'hero.btn_chat': 'Fale com nosso Chatbot',
    'hero.stat_products': 'Produtos',
    'hero.stat_support': 'Suporte',
    'hero.stat_languages': 'Idiomas',
    'hero.nav_products': 'Produtos',
    'hero.nav_contact': 'Contato',
    'hero.nav_catalog': 'Ver Catalogo',
    'catalog.title': 'Nossos Produtos',
    'catalog.desc': 'Explore nosso catalogo completo de notebooks e acessorios',
    'catalog.filter_all': 'Todos',
    'catalog.filter_laptops': 'Notebooks',
    'catalog.filter_accessories': 'Acessorios',
    'catalog.loading': 'Carregando produtos...',
    'catalog.section_laptops': 'Notebooks',
    'catalog.section_accessories': 'Acessorios',
    'card.add_cart': 'Adicionar ao Carrinho',
    'card.unavailable': 'Indisponivel',
    'card.in_stock': 'Em estoque',
    'card.low_stock': 'Apenas',
    'card.out_of_stock': 'Esgotado',
    'card.stock_remaining': 'restantes',
    'footer.desc': 'Sua loja de tecnologia com os melhores notebooks e acessorios do mercado.',
    'footer.links': 'Links',
    'footer.products': 'Produtos',
    'footer.contact': 'Contato',
    'footer.support': 'Suporte',
    'footer.support_desc': 'Chatbot disponivel 24/7 em Portugues, Espanhol e Ingles.',
    'footer.email': 'Email: suporte@techstore.com',
    'footer.copyright': '2026 TechStore. Todos os direitos reservados. Projeto portfolio chatbot-as-a-service.',
    'chat.welcome': 'Ola! Sou o assistente da TechStore. Como posso ajudar voce?',
    'chat.placeholder': 'Digite sua mensagem...',
    'chat.error': 'Erro ao conectar. Tente novamente.',
    'app.admin_panel': 'Painel Admin',
    'app.logout': 'Sair',
    'app.logged_in': 'Logado como',
  },
  en: {
    'hero.badge': 'Latest generation technology',
    'hero.title1': 'Find the',
    'hero.title2': 'perfect notebook',
    'hero.title3': 'for you',
    'hero.desc': 'Gaming, professional and everyday laptops. Complete accessories, competitive prices and specialized technical support.',
    'hero.btn_products': 'Explore Products',
    'hero.btn_chat': 'Chat with our Bot',
    'hero.stat_products': 'Products',
    'hero.stat_support': 'Support',
    'hero.stat_languages': 'Languages',
    'hero.nav_products': 'Products',
    'hero.nav_contact': 'Contact',
    'hero.nav_catalog': 'View Catalog',
    'catalog.title': 'Our Products',
    'catalog.desc': 'Explore our complete catalog of notebooks and accessories',
    'catalog.filter_all': 'All',
    'catalog.filter_laptops': 'Notebooks',
    'catalog.filter_accessories': 'Accessories',
    'catalog.loading': 'Loading products...',
    'catalog.section_laptops': 'Notebooks',
    'catalog.section_accessories': 'Accessories',
    'card.add_cart': 'Add to Cart',
    'card.unavailable': 'Unavailable',
    'card.in_stock': 'In stock',
    'card.low_stock': 'Only',
    'card.out_of_stock': 'Out of stock',
    'card.stock_remaining': 'left',
    'footer.desc': 'Your technology store with the best notebooks and accessories on the market.',
    'footer.links': 'Links',
    'footer.products': 'Products',
    'footer.contact': 'Contact',
    'footer.support': 'Support',
    'footer.support_desc': 'Chatbot available 24/7 in Portuguese, Spanish and English.',
    'footer.email': 'Email: support@techstore.com',
    'footer.copyright': '2026 TechStore. All rights reserved. Chatbot-as-a-service portfolio project.',
    'chat.welcome': 'Hello! I am the TechStore assistant. How can I help you?',
    'chat.placeholder': 'Type your message...',
    'chat.error': 'Connection error. Please try again.',
    'app.admin_panel': 'Admin Panel',
    'app.logout': 'Sign Out',
    'app.logged_in': 'Logged in as',
  },
}

const LanguageContext = createContext<LanguageContextType>({
  lang: 'es',
  setLang: () => {},
  t: (key: string) => key,
})

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    const saved = localStorage.getItem('lang') as Lang
    if (saved && ['es', 'pt', 'en'].includes(saved)) return saved
    const browserLang = navigator.language.toLowerCase()
    if (browserLang.startsWith('pt')) return 'pt'
    if (browserLang.startsWith('en')) return 'en'
    return 'es'
  })

  useEffect(() => {
    localStorage.setItem('lang', lang)
    document.documentElement.lang = lang
  }, [lang])

  const setLang = (l: Lang) => setLangState(l)

  const t = (key: string): string => {
    return translations[lang][key] || translations['es'][key] || key
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  return useContext(LanguageContext)
}

