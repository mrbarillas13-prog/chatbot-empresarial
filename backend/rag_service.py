import chromadb
from sqlalchemy.orm import Session
from app.models import Product

client = chromadb.PersistentClient(path="/chroma_data")

try:
    collection = client.get_collection("products")
except Exception:
    collection = client.create_collection("products")


def index_products(db: Session):
    products = db.query(Product).all()
    if not products:
        return 0

    ids = []
    documents = []
    metadatas = []

    for p in products:
        doc = f"{p.name}. {p.description or ''} Categoria: {p.category or 'N/A'}. Precio: {p.price:.2f} EUR. Stock: {p.stock} unidades."
        meta = {
            "name": p.name,
            "price": p.price,
            "category": p.category or "N/A",
            "stock": p.stock,
            "description": p.description or "",
            "product_id": str(p.id),
        }
        ids.append(str(p.id))
        documents.append(doc)
        metadatas.append(meta)

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(products)


def search_semantic(query: str, n_results: int = 5) -> list[dict]:
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
    except Exception:
        return []

    if not results or not results["documents"][0]:
        return []

    products = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        distance = results["distances"][0][i] if results["distances"] else 0
        products.append({
            "name": meta.get("name", "Unknown"),
            "price": meta.get("price", 0),
            "category": meta.get("category", "N/A"),
            "stock": meta.get("stock", 0),
            "description": meta.get("description", ""),
            "product_id": meta.get("product_id", ""),
            "relevance": max(0, 1 - distance),
        })

    return products


def get_recommendations(query: str, n_results: int = 3) -> str:
    products = search_semantic(query, n_results)
    if not products:
        return "No encontre productos relacionados con tu busqueda."

    lines = ["PRODUCTOS RECOMENDADOS (busqueda semantica):"]
    for p in products:
        stock_status = "Disponible" if p["stock"] > 0 else "Agotado"
        relevance_pct = int(p["relevance"] * 100)
        lines.append(
            f"- {p['name']} | {p['price']:.2f} | {p['category']} | "
            f"Stock: {p['stock']} ({stock_status}) | Relevancia: {relevance_pct}%"
        )
    return "\n".join(lines)


def get_dynamic_context(message: str, db: Session) -> str:
    products = search_semantic(message, n_results=5)
    if not products:
        return ""

    available = [p for p in products if p["stock"] > 0]
    if not available:
        return "No hay productos disponibles relacionados con tu consulta."

    lines = ["CONTEXTO RELEVANTE (busqueda semantica):"]
    for p in available:
        lines.append(
            f"- {p['name']} ({p['category']}): {p['price']:.2f}, "
            f"{p['stock']} unidades disponibles. {p['description']}"
        )
    return "\n".join(lines)


def get_category_recommendations(category: str) -> str:
    products = search_semantic(category, n_results=10)
    if not products:
        return f"No encontre productos en la categoria '{category}'."

    category_lower = category.lower()
    filtered = [p for p in products if p["category"].lower() == category_lower]
    if not filtered:
        filtered = products

    lines = [f"PRODUCTOS EN CATEGORIA '{category.upper()}':"]
    for p in filtered:
        lines.append(f"- {p['name']} | {p['price']:.2f} | Stock: {p['stock']}")
    return "\n".join(lines)


def get_stock_info(query: str) -> str:
    products = search_semantic(query, n_results=5)
    if not products:
        return "No encontre productos para consultar stock."

    lines = ["INFORMACION DE STOCK:"]
    for p in products:
        status = "Disponible" if p["stock"] > 0 else "Agotado"
        lines.append(f"- {p['name']}: {p['stock']} unidades ({status})")
    return "\n".join(lines)


