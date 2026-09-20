export default function Footer() {
  return (
    <footer id="contato" className="bg-gray-900 text-white py-12 px-6 lg:px-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-cyan-400 rounded-lg flex items-center justify-center font-bold text-blue-900">T</div>
            <span className="text-lg font-bold">TechStore</span>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed">
            Sua loja de tecnologia com os melhores notebooks e acessórios do mercado.
          </p>
        </div>
        <div>
          <h4 className="font-bold mb-4">Links</h4>
          <ul className="space-y-2 text-gray-400 text-sm">
            <li><a href="#productos" className="hover:text-cyan-400 transition">Produtos</a></li>
            <li><a href="#contato" className="hover:text-cyan-400 transition">Contato</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold mb-4">Suporte</h4>
          <p className="text-gray-400 text-sm">Chatbot disponível 24/7 em Português, Espanhol e Inglês.</p>
          <p className="text-gray-400 text-sm mt-2">Email: suporte@techstore.com</p>
        </div>
      </div>
      <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
        2026 TechStore. Todos os direitos reservados. Projeto portfolio chatbot-as-a-service.
      </div>
    </footer>
  )
}


