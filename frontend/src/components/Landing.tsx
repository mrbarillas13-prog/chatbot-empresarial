import { useState } from 'react'
import Hero from './Hero'
import ProductCatalog from './ProductCatalog'
import ChatWidget from './ChatWidget'
import Footer from './Footer'

export default function Landing() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Hero />
      <ProductCatalog />
      <Footer />
      <ChatWidget />
    </div>
  )
}
