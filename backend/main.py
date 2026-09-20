from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from uuid import UUID
import os

from database import get_db, engine, Base
from app.models import Product, Order, OrderItem, Ticket, Conversation
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductList
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderList
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketList
from app.schemas.chat import ChatRequest, ChatResponse
from chat_service import chat_with_ai, classify_intent, summarize_conversation
from rag_service import index_products, search_semantic
from app.api.auth import router as auth_router
from app.services.auth_service import get_current_user
from email_service import send_order_confirmation

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chatbot Empresarial API",
    description="API para chatbot empresarial con RAG",
    version="1.0.0"
)


@app.on_event("startup")
def startup_index():
    db = Session(bind=engine)
    try:
        count = index_products(db)
        print(f"RAG: {count} productos indexados en ChromaDB")
    finally:
        db.close()

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Chatbot Empresarial API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/products", response_model=ProductList)
def list_products(
    search: str = None,
    category: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    if category:
        query = query.filter(Product.category == category)
    total = query.count()
    products = query.offset(offset).limit(limit).all()
    return {"products": products, "total": total}


@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@app.post("/api/orders", response_model=OrderResponse)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        status="pending",
        total=sum(item.unit_price * item.quantity for item in order.items)
    )
    db.add(db_order)
    db.flush()

    for item in order.items:
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/api/orders", response_model=OrderList)
def list_orders(
    email: str = None,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")
    
    query = db.query(Order)
    if email:
        query = query.filter(Order.customer_email == email)
    if status:
        query = query.filter(Order.status == status)
    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(limit).all()
    return {"orders": orders, "total": total}


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order


@app.put("/api/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: UUID, order_update: OrderUpdate, authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden cambiar estado de pedidos")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if order_update.status:
        order.status = order_update.status
    db.commit()
    db.refresh(order)
    return order


@app.post("/api/tickets", response_model=TicketResponse)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    db_ticket = Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@app.get("/api/tickets", response_model=TicketList)
def list_tickets(
    email: str = None,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Ticket)
    if email:
        query = query.filter(Ticket.customer_email == email)
    if status:
        query = query.filter(Ticket.status == status)
    total = query.count()
    tickets = query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()
    return {"tickets": tickets, "total": total}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    intent = classify_intent(request.message)
    
    context = ""
    if intent == "consulta_producto":
        products = search_semantic(request.message, n_results=3)
        if products:
            context = "Productos encontrados: " + str(products)
    elif intent == "consulta_pedido":
        context = "El cliente consulta por su pedido."
    elif intent == "crear_ticket":
        context = "El cliente quiere crear un ticket de soporte."
    
    result = chat_with_ai(request.session_id, request.message, context, db)
    reply = result["reply"]
    order_data = result.get("order")
    
    if order_data:
        send_order_confirmation(
            to_email=order_data["email"],
            customer_name=order_data["name"],
            order_id=order_data["order_id"],
            product_name=order_data["product_name"],
            total=order_data["total"]
        )
    
    conversation = Conversation(
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    db.add(conversation)
    
    conversation_reply = Conversation(
        session_id=request.session_id,
        role="assistant",
        content=reply
    )
    db.add(conversation_reply)
    db.commit()
    
    return ChatResponse(
        reply=reply,
        session_id=request.session_id,
        intent=intent
    )


@app.get("/api/conversations/{session_id}")
def get_conversation(session_id: str, db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(
        Conversation.session_id == session_id
    ).order_by(Conversation.created_at).all()
    return {"conversations": conversations}


@app.post("/api/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    index_products(db)
    return db_product


@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: UUID, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    index_products(db)
    return db_product


@app.delete("/api/products/{product_id}")
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_product)
    db.commit()
    index_products(db)
    return {"message": "Producto eliminado"}


@app.get("/api/search")
def search_products(q: str, db: Session = Depends(get_db)):
    results = search_semantic(q, n_results=5)
    return {"query": q, "results": results}


@app.post("/api/voice/webhook")
def voice_webhook(data: dict, db: Session = Depends(get_db)):
    query = data.get("query", "")
    intent = data.get("intent", "search")
    
    if intent == "search" or intent == "producto":
        results = search_semantic(query, n_results=3)
        if results:
            products_text = []
            for p in results:
                products_text.append(f"{p['name']} - ${p['price']} - Stock: {p['stock']} unidades")
            return {
                "response": f"Encontré estos productos: {', '.join(products_text)}",
                "products": results
            }
        else:
            return {"response": "No encontré productos para esa consulta.", "products": []}
    
    elif intent == "stock":
        products = db.query(Product).filter(
            Product.name.ilike(f"%{query}%")
        ).all()
        if products:
            stock_info = []
            for p in products:
                stock_info.append(f"{p.name}: {p.stock} unidades disponibles")
            return {"response": f"Stock disponible: {', '.join(stock_info)}", "products": []}
        return {"response": "No encontré ese producto en nuestro catálogo.", "products": []}
    
    elif intent == "pedido":
        return {"response": "Para consultar tu pedido, necesito tu número de email. ¿Cuál es tu email?", "products": []}
    
    elif intent == "soporte":
        return {"response": "Entiendo que tienes un problema. Puedo ayudarte a crear un ticket de soporte. ¿Cuál es el problema?", "products": []}
    
    else:
        products = db.query(Product).limit(5).all()
        products_list = [f"{p.name} - ${p.price}" for p in products]
        return {
            "response": f"Somos TechStore. Tenemos estos productos destacados: {', '.join(products_list)}. ¿En qué puedo ayudarte?",
            "products": []
        }


@app.get("/api/voice/products")
def voice_products(db: Session = Depends(get_db)):
    products = db.query(Product).limit(20).all()
    products_list = []
    for p in products:
        products_list.append({
            "name": p.name,
            "price": p.price,
            "category": p.category,
            "stock": p.stock,
            "description": p.description or ""
        })
    return {"products": products_list}


@app.get("/api/catalog")
def public_catalog(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    result = []
    for p in products:
        result.append({
            "id": str(p.id),
            "name": p.name,
            "name_pt": getattr(p, "name_pt", None),
            "description": p.description,
            "description_pt": getattr(p, "description_pt", None),
            "price": p.price,
            "category": p.category,
            "stock": p.stock,
            "image_url": getattr(p, "image_url", None)
        })
    return result
