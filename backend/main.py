from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
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


# === PRODUCTS ===
@app.get("/api/products", response_model=ProductList)
def list_products(
    search: str = None,
    category: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Product.category == category)
    total = query.count()
    products = query.offset(offset).limit(limit).all()
    return ProductList(products=products, total=total)


@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/api/products", response_model=ProductResponse)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.put("/api/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: UUID, product_data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/api/products/{product_id}")
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"detail": "Product deleted"}


# === ORDERS ===
@app.get("/api/orders", response_model=OrderList)
def list_orders(
    email: str = None,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Order)
    if email:
        query = query.filter(Order.customer_email == email)
    if status:
        query = query.filter(Order.status == status)
    total = query.count()
    orders = query.offset(offset).limit(limit).all()
    return OrderList(orders=orders, total=total)


@app.post("/api/orders", response_model=OrderResponse)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    total = sum(item.quantity * item.unit_price for item in order_data.items)
    order = Order(
        customer_name=order_data.customer_name,
        customer_email=order_data.customer_email,
        total=total,
    )
    db.add(order)
    db.flush()
    for item in order_data.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        db.add(order_item)
    db.commit()
    db.refresh(order)
    return order


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/api/orders/{order_id}", response_model=OrderResponse)
def update_order(order_id: UUID, order_data: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    update_data = order_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


@app.delete("/api/orders/{order_id}")
def delete_order(order_id: UUID, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"detail": "Order deleted"}


# === TICKETS ===
@app.get("/api/tickets", response_model=TicketList)
def list_tickets(
    email: str = None,
    status: str = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Ticket)
    if email:
        query = query.filter(Ticket.customer_email == email)
    if status:
        query = query.filter(Ticket.status == status)
    total = query.count()
    tickets = query.offset(offset).limit(limit).all()
    return TicketList(tickets=tickets, total=total)


@app.post("/api/tickets", response_model=TicketResponse)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    ticket = Ticket(**ticket_data.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/api/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.put("/api/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: UUID, ticket_data: TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    update_data = ticket_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.delete("/api/tickets/{ticket_id}")
def delete_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return {"detail": "Ticket deleted"}


# === CHAT ===
@app.post("/api/chat", response_model=ChatResponse)
def chat(message: ChatRequest, db: Session = Depends(get_db)):
    user_msg = Conversation(
        session_id=message.session_id,
        role="user",
        content=message.message,
    )
    db.add(user_msg)
    db.flush()

    intent = classify_intent(message.message)
    reply = chat_with_ai(message.message, message.session_id, db)

    assistant_msg = Conversation(
        session_id=message.session_id,
        role="assistant",
        content=reply,
        metadata_={"intent": intent},
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        reply=reply,
        session_id=message.session_id,
        action=intent,
    )


@app.get("/api/conversations/{session_id}")
def get_conversation(session_id: str, limit: int = 50, db: Session = Depends(get_db)):
    messages = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at)
        .limit(limit)
        .all()
    )
    return {"session_id": session_id, "messages": messages}


@app.get("/api/conversations/{session_id}/summarize")
def summarize(session_id: str, db: Session = Depends(get_db)):
    summary = summarize_conversation(session_id, db)
    return {"session_id": session_id, "summary": summary}


# === RAG ===
@app.post("/api/rag/reindex")
def reindex(db: Session = Depends(get_db)):
    count = index_products(db)
    return {"message": f"{count} productos indexados en ChromaDB"}


@app.get("/api/rag/search")
def rag_search(q: str, n: int = 5):
    results = search_semantic(q, n_results=n)
    return {"query": q, "results": results, "count": len(results)}
