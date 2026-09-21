import os
import re
from openai import OpenAI
from sqlalchemy.orm import Session
from app.models import Product, Conversation, Order, OrderItem
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


def detect_language(message: str) -> str:
    pt_words = ["ola", "oi", "bom", "dia", "noite", "obrigado", "obrigada", "por favor",
                "quais", "tem", "temos", "quanto", "preco", "preco", "notebook", "notebooks",
                "celular", "fone", "mouse", "teclado", "webcam", "parlante", "cabo",
                "adaptador", "organizador", "funda", "bolsa", "base", "suporte",
                "comprar", "compra", "quero", "gostaria", "pode", "como", "onde",
                "qual", "quais", "algum", "alguma", "gamer", "profissional",
                "lancamento", "chegou", "disponivel", "estoque", "restam"]
    en_words = ["hello", "hi", "hey", "good", "morning", "evening", "thanks", "please",
                "which", "what", "how", "much", "price", "laptop", "laptops",
                "phone", "headphone", "mouse", "keyboard", "webcam", "speaker", "cable",
                "adapter", "organizer", "case", "bag", "stand", "holder",
                "buy", "purchase", "want", "would", "can", "how", "where",
                "any", "some", "gaming", "professional",
                "available", "stock", "left", "have"]
    msg_lower = message.lower()
    pt_count = sum(1 for w in pt_words if w in msg_lower)
    en_count = sum(1 for w in en_words if w in msg_lower)
    if pt_count > en_count:
        return "pt"
    elif en_count > pt_count:
        return "en"
    return "es"


def get_system_prompt(lang: str) -> str:
    prompts = {
        "es": """Eres el asistente virtual de una tienda de tecnologia llamada "TechStore".
Tu trabajo es ayudar a los clientes con informacion sobre productos, precios, stock, pedidos y soporte.

REGLAS:
- Responde en espanol, de forma amigable y profesional. Usa euros (EUR) para precios, NUNCA dolares.
- Usa la informacion de productos que te doy como contexto para responder.
- Si no tienes informacion sobre algo, di la verdad: "No tengo esa informacion, pero puedo conectarte con soporte."
- Puedes buscar productos por nombre, caracteristicas o necesidad del cliente.
- Puedes decirle al cliente si un producto esta en stock o no.
- Recomienda productos relevantes cuando sea apropiado.
- Se conciso: respuestas de maximo 3-4 oraciones salvo que pidan mas detalle.
- NUNCA inventes pedidos, numeros de pedido, productos comprados ni estados. Solo puedes hablar de un pedido si aparece
  en el contexto como PEDIDO REAL. Si no aparece, di que no encuentras ningun pedido con esos datos y pide el email de la compra.

FLUJO DE COMPRA:
Cuando el cliente quiera comprar algo, pide su nombre y email.
Cuando te dé nombre y email, confirma los productos y precios, y responde confirmando que la orden fue creada con el ID del pedido.
IMPORTANTE: Cuando el cliente proporcione nombre Y email juntos en un solo mensaje, crea la orden automaticamente sin pedir confirmacion adicional.""",
        "pt": """Voce e o assistente virtual de uma loja de tecnologia chamada "TechStore".
Seu trabalho e ajudar clientes com informacoes sobre produtos, precos, estoque, pedidos e suporte.

REGRAS:
- Responda em portugues, de forma amigavel e profissional. Use euros (EUR) para precos, NUNCA dolares.
- Use as informacoes dos produtos que voce recebe como contexto para responder.
- Se nao tem informacao sobre algo, diga a verdade: "Nao tenho essa informacao, mas posso conectar voce com o suporte."
- Voce pode buscar produtos por nome, caracteristicas ou necessidade do cliente.
- Voce pode dizer ao cliente se um produto esta em estoque ou nao.
- Recomende produtos relevantes quando apropriado.
- Seja conciso: respostas de no maximo 3-4 frases, salvo que peçam mais detalhes.
- NUNCA invente pedidos, numeros de pedido, produtos comprados nem estados. So pode falar de um pedido se ele aparecer
  no contexto como PEDIDO REAL. Se nao aparecer, diga que nao encontra nenhum pedido com esses dados e peça o email da compra.

FLUXO DE COMPRA:
Quando o cliente quiser comprar algo, peca nome e email.
Quando o cliente der nome e email, confirme os produtos e precos, e responda confirmando que o pedido foi criado com o ID do pedido.
IMPORTANTE: Quando o cliente fornecer nome e email juntos em uma so mensagem, crie o pedido automaticamente sem pedir confirmacao adicional.""",
        "en": """You are the virtual assistant of a technology store called "TechStore".
Your job is to help customers with product information, prices, stock, orders, and support.

RULES:
- Respond in English, in a friendly and professional manner. Use euros (EUR) for prices, NEVER dollars.
- Use the product information provided as context to answer.
- If you don't have information about something, be honest: "I don't have that information, but I can connect you with support."
- You can search products by name, features, or customer needs.
- You can tell the customer if a product is in stock or not.
- Recommend relevant products when appropriate.
- Be concise: responses of max 3-4 sentences unless they ask for more detail.
- NEVER invent orders, order numbers, purchased products or statuses. You may only talk about an order if it appears
  in the context as a REAL ORDER. If it does not, say you cannot find any order with those details and ask for the purchase email.

PURCHASE FLOW:
When the customer wants to buy something, ask for their name and email.
When they provide name and email, confirm products and prices, and respond confirming the order was created with the order ID.
IMPORTANT: When the customer provides name AND email together in one message, create the order automatically without asking for additional confirmation."""
    }
    return prompts.get(lang, prompts["es"])


def format_products_for_context(products, lang: str) -> str:
    if not products:
        return ""
    lines = []
    for p in products:
        if lang == "pt":
            name = p.name_pt if p.name_pt else p.name
            desc = p.description_pt if p.description_pt else p.description
        elif lang == "en":
            name = p.name
            desc = p.description
        else:
            name = p.name
            desc = p.description
        lines.append(f"- {name}: {p.price} EUR ({p.stock} em estoque) - {desc}")
    return "\n".join(lines)


def classify_intent(message: str) -> str:
    msg = message.lower()
    stock_words = ["stock", "disponible", "queda", "hay", "cantidad", "agotado", "inventario",
                   "estoque", "disponivel", "restam", "esgotado"]
    search_words = ["buscar", "busca", "tienen", "hay algun", "catalogo", "mostrar", "lista", "ver productos", "que tienen",
                    "procurar", "tem", "temos", "catalogo", "mostrar", "lista", "ver produtos",
                    "search", "find", "do you have", "show", "list", "available"]
    category_words = ["categoria", "electronica", "accesorios", "audio", "almacenamiento", "mobiliario",
                      "laptops", "notebooks", "accessories"]
    order_words = ["pedido", "orden", "compra", "envio", "entrega", "donde esta mi",
                   "pedido", "compra", "envio", "entrega", "onde esta meu",
                   "order", "purchase", "shipping", "delivery", "where is my"]
    summary_words = ["resumen", "resumir", "que hablamos", "hasta ahora",
                     "resumo", "resumir", "o que falamos",
                     "summary", "summarize", "what did we talk"]
    ticket_words = ["soporte", "problema", "queja", "reclamo", "garantia", "ayuda con",
                    "suporte", "problema", "reclamacao", "garantia", "ajuda com",
                    "support", "problem", "complaint", "warranty", "help with"]
    recommend_words = ["recomendar", "recomienda", "que me lleva", "algo para", "necesito", "busco algo", "que me sugiere",
                       "recomendar", "recomenda", "o que leva", "algo para", "preciso", "procuro algo",
                       "recommend", "suggest", "what should I get", "something for", "I need", "looking for"]
    buy_words = ["comprar", "compra", "quiero", "llevar", "adicionar", "carrito", "carro", "cesta", "pagar",
                 "comprar", "compra", "quero", "levar", "adicionar", "carrinho", "cesta", "pagar",
                 "buy", "purchase", "want", "add to cart", "cart", "checkout", "pay"]

    if any(w in msg for w in buy_words):
        return "add_to_cart"
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


def extract_email(text: str) -> str:
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else None


def extract_name(text: str, lang: str) -> str:
    patterns = {
        "es": [
            r'me llamo\s+([A-Za-z\u00C0-\u024F]+(?:\s+[A-Za-z\u00C0-\u024F]+)*)',
            r'mi nombre es\s+([A-Za-z\u00C0-\u024F]+(?:\s+[A-Za-z\u00C0-\u024F]+)*)',
            r'soy\s+([A-Za-z\u00C0-\u024F]+(?:\s+[A-Za-z\u00C0-\u024F]+)*)',
            r'se llama\s+([A-Za-z\u00C0-\u024F]+(?:\s+[A-Za-z\u00C0-\u024F]+)*)',
        ],
        "pt": [
            r'me chamo\s+([A-Za-z\u00C0-\u024F]+(?:\s+[A-Za-z\u00C0-\u024F]+)*)',
            r'meu nome e\s+([A-Za-z\u00C0-\u024F]+(?:\s+[A-Za-z\u00C0-\u024F]+)*)',
            r'sou\s+([A-Za-z\u00C0-\u024F]+(?:\s+[A-Za-z\u00C0-\u024F]+)*)',
        ],
        "en": [
            r'my name is\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            r"i'm\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
            r"i am\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
            r"call me\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)",
        ],
    }
    for pattern in patterns.get(lang, patterns["es"]):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def has_recent_purchase_intent(session_id: str, db: Session, limit: int = 8) -> bool:
    """True solo si en los ultimos mensajes del usuario hay intencion clara de COMPRA."""
    for msg in get_recent_history(session_id, db, limit=limit):
        if msg["role"] == "user" and classify_intent(msg["content"]) == "add_to_cart":
            return True
    return False


NAME_STOPWORDS = {
    "sim", "nao", "no", "ok", "okay", "si", "yes", "obrigado", "obrigada", "gracias", "thanks",
    "thank", "you", "bom", "boa", "dia", "tarde", "noite", "hello", "ola", "quero", "quiero",
    "comprar", "buy", "order", "pedido", "por", "favor", "please", "confirmo", "confirma", "certo",
    "notebook", "laptop", "producto", "produto", "product",
}


def find_name_in_history(session_id: str, db: Session, limit: int = 10) -> str:
    """El cliente suele dar el nombre suelto ("Pedro Perez"). Lo busca en los ultimos mensajes."""
    for msg in get_recent_history(session_id, db, limit=limit):
        if msg["role"] != "user":
            continue
        text = (msg["content"] or "").strip()
        if "@" in text or any(ch.isdigit() for ch in text) or len(text) > 40:
            continue
        words = text.split()
        if not (1 <= len(words) <= 3):
            continue
        if not all(re.fullmatch(r"[A-Za-z\u00C0-\u024F'.-]+", w) for w in words):
            continue
        if any(w.lower() in NAME_STOPWORDS for w in words):
            continue
        return " ".join(w.capitalize() for w in words)
    return ""


def find_orders_for_customer(email: str, db: Session, limit: int = 5) -> list:
    """Pedidos REALES de un email. SOLO LECTURA: no crea ni modifica nada."""
    from sqlalchemy import func
    return (db.query(Order)
            .filter(func.lower(Order.customer_email) == email.strip().lower())
            .order_by(Order.created_at.desc())
            .limit(limit)
            .all())


def _items_summary(order, db: Session) -> str:
    try:
        items = list(order.items or [])
    except Exception:
        return ""
    if not items:
        return ""
    ids = [it.product_id for it in items]
    names = {str(p.id): p.name for p in db.query(Product).filter(Product.id.in_(ids)).all()}
    return ", ".join(f"{it.quantity}x {names.get(str(it.product_id), 'produto')}" for it in items)


def format_orders_for_context(orders: list, db: Session, lang: str) -> str:
    """Contexto con los pedidos reales del cliente, o el aviso de que no hay ninguno."""
    if not orders:
        if lang == "pt":
            return ("PEDIDOS REAIS: nenhum. Nao existe nenhum pedido com esse email. Diga ao cliente que nao encontra "
                    "nenhum pedido com esses dados e peça o email usado na compra. Nao invente nada.")
        if lang == "en":
            return ("REAL ORDERS: none. There is no order with that email. Tell the customer you cannot find any order "
                    "with those details and ask for the email used in the purchase. Do not invent anything.")
        return ("PEDIDOS REALES: ninguno. No existe ningun pedido con ese email. Dile al cliente que no encuentras ningun "
                "pedido con esos datos y pide el email usado en la compra. No inventes nada.")
    header = {
        "pt": "PEDIDOS REAIS deste cliente (use SOMENTE estes dados, nao invente):",
        "en": "REAL ORDERS for this customer (use ONLY this data, do not invent):",
    }.get(lang, "PEDIDOS REALES de este cliente (usa SOLO estos datos, no inventes):")
    lines = []
    for o in orders:
        prod = _items_summary(o, db)
        lines.append(f"- ID {str(o.id)[:8]} | {o.customer_name} | {prod} | {o.total:.2f} EUR | estado: {o.status} | {str(o.created_at)[:10]}")
    return header + "\n" + "\n".join(lines)


def get_context_for_intent(intent: str, message: str, db: Session) -> tuple:
    lang = detect_language(message)

    if intent == "search":
        return get_dynamic_context(message, db), lang

    if intent == "category":
        return get_dynamic_context(message, db), lang

    if intent == "stock":
        return get_stock_info(message), lang

    if intent == "recommend":
        return get_recommendations(message, n_results=5), lang

    if intent == "order":
        if lang == "pt":
            return "O cliente pergunta sobre um pedido. Informe que pode fornecer seu email para verificar o status.", lang
        elif lang == "en":
            return "The customer is asking about an order. Inform them they can provide their email to check the status.", lang
        return "El cliente pregunta sobre un pedido. Informa que puede proporcionar su email para revisar el estado.", lang

    if intent == "ticket":
        if lang == "pt":
            return "O cliente precisa de suporte. Sugira criar um ticket com: nome, email, assunto e descricao.", lang
        elif lang == "en":
            return "The customer needs support. Suggest creating a ticket with: name, email, subject, and description.", lang
        return "El cliente necesita soporte. Sugiere crear un ticket con: nombre, email, asunto y descripcion.", lang

    if intent == "add_to_cart":
        products = search_semantic(message, n_results=3)
        context = ""
        if products:
            context = "Productos encontrados: " + str(products)
        if lang == "pt":
            return f"O cliente quer comprar algo. Produtos encontrados: {context}\n\nQuando o cliente der nome e email, crie o pedido automaticamente.", lang
        elif lang == "en":
            return f"The customer wants to buy something. Products found: {context}\n\nWhen the customer provides name and email, create the order automatically.", lang
        return f"El cliente quiere comprar algo. Productos encontrados: {context}\n\nCuando el cliente dé nombre y email, crea la orden automáticamente.", lang

    return get_dynamic_context(message, db), lang


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


def try_create_order_from_chat(session_id: str, message: str, db: Session) -> dict:
    lang = detect_language(message)
    email = extract_email(message)
    name = extract_name(message, lang)

    if not email:
        return None

    history = get_recent_history(session_id, db, limit=20)
    product_name = None
    product_price = None
    product_id = None

    # Search all user messages for product references
    for msg in history:
        if msg["role"] == "user":
            products = search_semantic(msg["content"], n_results=1)
            if products:
                product_name = products[0].get("name")
                product_price = products[0].get("price")
                product_id = products[0].get("product_id") or products[0].get("id")
                break

    # Also search current message
    if not product_id:
        products = search_semantic(message, n_results=1)
        if products:
            product_name = products[0].get("name")
            product_price = products[0].get("price")
            product_id = products[0].get("product_id") or products[0].get("id")

    if not product_id:
        return None

    if not name:
        name = find_name_in_history(session_id, db)

    if not name:
        # Sin nombre real no se crea el pedido: el asistente lo pedira en la conversacion.
        return None

    try:
        from uuid import UUID
        product_uuid = UUID(product_id)
    except:
        return None

    db_order = Order(
        customer_name=name,
        customer_email=email,
        status="pending",
        total=product_price
    )
    db.add(db_order)
    db.flush()

    db_item = OrderItem(
        order_id=db_order.id,
        product_id=product_uuid,
        quantity=1,
        unit_price=product_price
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_order)

    return {
        "order_id": str(db_order.id),
        "product_name": product_name,
        "total": product_price,
        "email": email,
        "name": name,
        "lang": lang
    }


def chat_with_ai(session_id: str, message: str, context: str, db: Session) -> dict:
    if not client:
        return {"reply": "Error: La API key de DeepSeek no esta configurada.", "order": None}

    intent = classify_intent(message)
    context, lang = get_context_for_intent(intent, message, db)
    system_prompt = get_system_prompt(lang)
    history = get_recent_history(session_id, db)

    order_result = None
    status_context = None

    email_in_message = extract_email(message)
    purchase_in_progress = (intent == "add_to_cart") or has_recent_purchase_intent(session_id, db)

    if email_in_message and purchase_in_progress:
        # ESCRITURA: solo con intencion de compra + email (+ nombre, dentro de la funcion).
        order_result = try_create_order_from_chat(session_id, message, db)
    elif email_in_message:
        # LECTURA: el cliente pregunta por su pedido. Nunca crea nada.
        status_context = format_orders_for_context(find_orders_for_customer(email_in_message, db), db, lang)

    messages = [{"role": "system", "content": system_prompt}]

    if context:
        messages.append({"role": "system", "content": f"CONTEXTO ACTUAL:\n{context}"})

    if status_context:
        messages.append({"role": "system", "content": status_context})

    if order_result:
        order_msg = f"ORDEN CREADA: ID={order_result['order_id']}, Producto={order_result['product_name']}, Total={order_result['total']} EUR, Email={order_result['email']}, Nombre={order_result['name']}"
        messages.append({"role": "system", "content": order_msg})

    messages.extend(history)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        return {"reply": reply, "order": order_result}
    except Exception as e:
        return {"reply": f"Lo siento, hubo un error al procesar tu mensaje. Error: {str(e)[:100]}", "order": None}


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
