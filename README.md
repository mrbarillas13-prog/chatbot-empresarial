# Chatbot Empresarial

Chatbot de atenci?n al cliente para un negocio con inventario, pedidos, soporte y b?squeda inteligente (RAG) usando DeepSeek.

**Demo en vivo:** https://chatbotexpertservice.online

## Funcionalidades
- Chat con IA (DeepSeek) que responde preguntas sobre productos, precios y stock
- Inventario de productos con categor?as
- Registro de pedidos con c?lculo autom?tico del total
- Tickets de soporte
- B?squeda sem?ntica (RAG con ChromaDB)
- Recomendaciones de productos

## Stack
- **Frontend:** React + Vite + TypeScript + Tailwind
- **Backend:** FastAPI (Python)
- **Base de datos:** PostgreSQL
- **IA:** DeepSeek API
- **RAG:** ChromaDB
- **Despliegue:** Docker + nginx + HTTPS (Let's Encrypt)

## Estructura
```
backend/   -> API FastAPI (productos, pedidos, tickets, chat, RAG)
frontend/  -> App React
docker-compose.yml
```

## C?mo ejecutar
1. Crear archivo `.env` con:
   ```
   DATABASE_URL=postgresql://user:pass@localhost:5432/chatbot
   DEEPSEEK_API_KEY=tu_clave_deepseek
   DB_PASSWORD=tu_password
   ```
2. Levantar servicios:
   ```
   docker-compose up --build
   ```

## Nota de seguridad
- Las claves API (DEEPSEEK_API_KEY, DB_PASSWORD) van SOLO en `.env` (ignorado por git). Nunca se suben al repositorio.

---
Proyecto de portfolio ? programador junior.
