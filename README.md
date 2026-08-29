# Chatbot Empresarial / Business Chatbot / Chatbot Empresarial

Chatbot de atención al cliente para un negocio con inventario, pedidos, soporte y búsqueda inteligente (RAG) usando DeepSeek.
Customer service chatbot for a business with inventory, orders, support and smart search (RAG) using DeepSeek.
Chatbot de atendimento ao cliente para um negócio com inventário, pedidos, suporte e pesquisa inteligente (RAG) usando DeepSeek.

**Demo en vivo / Live demo / Demo ao vivo:** https://chatbotexpertservice.online

---

## English

### Features
- AI chat (DeepSeek) answering questions about products, prices and stock
- Product inventory with categories
- Order management with automatic total calculation
- Support tickets
- Semantic search (RAG with ChromaDB)
- Product recommendations

### Stack
- **Frontend:** React + Vite + TypeScript + Tailwind
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **AI:** DeepSeek API
- **RAG:** ChromaDB
- **Deployment:** Docker + nginx + HTTPS (Let's Encrypt)

### How to run
1. Create a `.env` file with:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot
   DEEPSEEK_API_KEY=your_deepseek_key
   DB_PASSWORD=your_password
   ```
2. Start services:
   ```
   docker-compose up --build
   ```

---

## Español

### Funcionalidades
- Chat con IA (DeepSeek) que responde sobre productos, precios y stock
- Inventario de productos con categorías
- Registro de pedidos con cálculo automático del total
- Tickets de soporte
- Búsqueda semántica (RAG con ChromaDB)
- Recomendaciones de productos

### Stack
- **Frontend:** React + Vite + TypeScript + Tailwind
- **Backend:** FastAPI (Python)
- **Base de datos:** PostgreSQL
- **IA:** DeepSeek API
- **RAG:** ChromaDB
- **Despliegue:** Docker + nginx + HTTPS (Let's Encrypt)

### Cómo ejecutar
1. Crear un archivo `.env` con:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot
   DEEPSEEK_API_KEY=tu_clave_deepseek
   DB_PASSWORD=tu_password
   ```
2. Levantar servicios:
   ```
   docker-compose up --build
   ```

---

## Português

### Funcionalidades
- Chat com IA (DeepSeek) que responde sobre produtos, preços e estoque
- Inventário de produtos com categorias
- Registro de pedidos com cálculo automático do total
- Tickets de suporte
- Pesquisa semântica (RAG com ChromaDB)
- Recomendações de produtos

### Stack
- **Frontend:** React + Vite + TypeScript + Tailwind
- **Backend:** FastAPI (Python)
- **Banco de dados:** PostgreSQL
- **IA:** DeepSeek API
- **RAG:** ChromaDB
- **Implantação:** Docker + nginx + HTTPS (Let's Encrypt)

### Como executar
1. Criar um arquivo `.env` com:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot
   DEEPSEEK_API_KEY=sua_chave_deepseek
   DB_PASSWORD=sua_senha
   ```
2. Iniciar serviços:
   ```
   docker-compose up --build
   ```

---

## Seguridad / Security / Segurança
- Las claves API (DEEPSEEK_API_KEY, DB_PASSWORD) van SOLO en `.env` (ignorado por git). Nunca se suben.
- API keys (DEEPSEEK_API_KEY, DB_PASSWORD) go ONLY in `.env` (ignored by git). They are never uploaded.
- As chaves de API (DEEPSEEK_API_KEY, DB_PASSWORD) ficam SOMENTE no `.env` (ignorado pelo git). Nunca são enviadas.

---
Portfolio project — junior developer / Proyecto de portfolio — programador junior / Projeto de portfólio — programador júnior.
