import os
from openai import OpenAI
from sqlalchemy.orm import Session
from app.models import Product, Conversation
from rag_service import (
    get_dynamic_context,
    get_recommendations,
    get_category_recommendations,
    get_stock_info,
    search_semantic,
    index_products,
)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL) if DEEPSEEK_API_KEY else None

SYSTEM_PROMPT = """Eres el asistente virtual de una tienda de tecnologia llamada "TechStore". 
Tu trabajo es ayudar a los clientes con informacion sobre productos, precios, stock, pedidos y soporte.

REGLAS:
- Responde en espanol, de forma amigable y profesional.
- Usa la informacion de productos que te doy como contexto para responder.
- Si no tienes informacion sobre algo, di la verdad: "No tengo esa informacion, pero puedo conectarte con soporte."
- Puedes buscar productos por nombre, caracteristicas o necesidad del cliente.
- Puedes decirle al cliente si un producto esta en stock o no.
- Si te piden un resumen de la conversacion, resume los puntos clave.
- Recomienda productos relevantes cuando sea apropiado.
- Se conciso: respuestas de maximo 3-4 oraciones salvo que pidan mas detalle."""


def classify_intent(message: str) -> str:
    msg = message.lower()
    stock_words = ["stock", "disponible", "queda", "hay", "cantidad", "agotado", "inventario"]
    search_words = ["buscar", "busca", "tienen", "hay algun", "catalogo", "mostrar", "lista", "ver productos", "que tienen"]
    category_words = ["categoria", "electronica", "accesorios", "audio", "almacenamiento", "mobiliario"]
    order_words = ["pedido", "orden", "compra", "envio", "entrega", "donde esta mi"]
    summary_words = ["resumen", "resumir", "que hablamos", "hasta ahora"]
    ticket_words = ["soporte", "problema", "queja", "reclamo", "garantia", "ayuda con"]
    recommend_words = ["recomendar", "recomienda", "que me lleva", "algo para", "necesito", "busco algo", "que me sugiere"]

    if any(w in msg for w in stock_words):
        return "stock"
    if any(w in msg for w in summary_words):
        return "summary"
    if any(w in msg for w in order_words):
        return "order"
    if any(w in msg for w in ticket_words):
        return "ticket"
    if any(w in msg for w in recommend_words):
        return "recommend"
    if any(w in msg for w in category_words):
        return "category"
    if any(w in msg for w in search_words):
        return "search"
    return "general"


def get_context_for_intent(intent: str, message: str, db: Session) -> str:
    if intent == "search":
        return get_dynamic_context(message, db)

    if intent == "category":
        msg_lower = message.lower()
        category = None
        for cat in ["electronica", "accesorios", "audio", "almacenamiento", "mobiliario"]:
            if cat in msg_lower:
                category = cat.capitalize()
                break
        if category:
            return get_category_recommendations(category)
        return get_dynamic_context(message, db)

    if intent == "stock":
        return get_stock_info(message)

    if intent == "recommend":
        return get_recommendations(message, n_results=5)

    if intent == "order":
        return "El cliente pregunta sobre un pedido. Informa que puede proporcionar su email para revisar el estado."

    if intent == "ticket":
        return "El cliente necesita soporte. Sugiere crear un ticket con: nombre, email, asunto y descripcion."

    return get_dynamic_context(message, db)


def get_recent_history(session_id: str, db: Session, limit: int = 10) -> list:
    messages = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return [{"role": m.role, "content": m.content} for m in messages]


def chat_with_ai(message: str, session_id: str, db: Session) -> str:
    if not client:
        return "Error: La API key de DeepSeek no esta configurada."

    intent = classify_intent(message)
    context = get_context_for_intent(intent, message, db)
    history = get_recent_history(session_id, db)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context:
        messages.append({"role": "system", "content": f"CONTEXTO ACTUAL:\n{context}"})

    messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Lo siento, hubo un error al procesar tu mensaje. Error: {str(e)[:100]}"


def summarize_conversation(session_id: str, db: Session) -> str:
    messages = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at)
        .all()
    )
    if not messages:
        return "No hay mensajes en esta conversacion."

    if not client:
        convo_text = "\n".join(f"{m.role}: {m.content}" for m in messages)
        return f"Resumen manual ({len(messages)} mensajes):\n{convo_text[:500]}"

    convo_text = "\n".join(f"{m.role}: {m.content}" for m in messages)
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Resume esta conversacion en 3-5 puntos clave, en espanol."},
                {"role": "user", "content": convo_text},
            ],
            max_tokens=200,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error al generar resumen: {str(e)[:100]}"
