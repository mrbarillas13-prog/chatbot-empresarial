import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import engine, Base
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.ticket import Ticket
from app.models.conversation import Conversation


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)

    # Check if data already exists
    if db.query(Product).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    print("Seeding database...")

    # === PRODUCTS ===
    products = [
        Product(name="Laptop Pro 15", description="Laptop de 15 pulgadas con procesador Intel i7, 16GB RAM, 512GB SSD", price=1299.99, category="Electronica", stock=25),
        Product(name="Mouse Inalambrico", description="Mouse ergonomico inalambrico con sensor optico 1600 DPI", price=29.99, category="Accesorios", stock=150),
        Product(name="Teclado Mecanico RGB", description="Teclado mecanico con switches Cherry MX Blue y retroiluminacion RGB", price=89.99, category="Accesorios", stock=75),
        Product(name="Monitor 27\" 4K", description="Monitor IPS 27 pulgadas resolucion 4K UHD, 60Hz", price=449.99, category="Electronica", stock=30),
        Product(name="Auriculares Bluetooth", description="Auriculares inalambricos con cancelacion de ruido activa", price=199.99, category="Audio", stock=60),
        Product(name="Webcam HD 1080p", description="Webcam Full HD con microfono integrado y autoenfoque", price=79.99, category="Accesorios", stock=45),
        Product(name="Hub USB-C 7-en-1", description="Hub USB-C con HDMI, USB-A, SD card, y carga rapida", price=49.99, category="Accesorios", stock=100),
        Product(name="Disco Duro SSD 1TB", description="SSD NVMe de 1TB con velocidades de lectura 3500MB/s", price=109.99, category="Almacenamiento", stock=80),
        Product(name="Silla Ergonomica", description="Silla de oficina ergonomica con soporte lumbar ajustable", price=349.99, category="Mobiliario", stock=20),
        Product(name="Webcam Ring Light", description="Ring light de 10 pulgarias con soporte para webcam y telefono", price=39.99, category="Accesorios", stock=90),
    ]

    db.add_all(products)
    db.flush()
    print(f"  - {len(products)} products created")

    # === ORDERS ===
    orders_data = [
        {
            "customer_name": "Carlos Martinez",
            "customer_email": "carlos@empresa.com",
            "status": "delivered",
            "items": [(products[0].id, 1, 1299.99), (products[1].id, 2, 29.99)],
        },
        {
            "customer_name": "Maria Garcia",
            "customer_email": "maria@startup.io",
            "status": "shipped",
            "items": [(products[3].id, 1, 449.99), (products[4].id, 1, 199.99)],
        },
        {
            "customer_name": "Juan Lopez",
            "customer_email": "juan@correo.com",
            "status": "pending",
            "items": [(products[2].id, 1, 89.99), (products[6].id, 3, 49.99)],
        },
        {
            "customer_name": "Ana Rodriguez",
            "customer_email": "ana@techcorp.com",
            "status": "delivered",
            "items": [(products[8].id, 2, 349.99)],
        },
        {
            "customer_name": "Pedro Sanchez",
            "customer_email": "pedro@digital.com",
            "status": "cancelled",
            "items": [(products[7].id, 1, 109.99)],
        },
    ]

    for i, order_data in enumerate(orders_data):
        order = Order(
            customer_name=order_data["customer_name"],
            customer_email=order_data["customer_email"],
            status=order_data["status"],
            total=sum(qty * price for _, qty, price in order_data["items"]),
            created_at=datetime.utcnow() - timedelta(days=10 - i),
        )
        db.add(order)
        db.flush()

        for product_id, qty, unit_price in order_data["items"]:
            item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
            )
            db.add(item)

    print(f"  - {len(orders_data)} orders created")

    # === TICKETS ===
    tickets = [
        Ticket(
            customer_name="Carlos Martinez",
            customer_email="carlos@empresa.com",
            subject="Laptop no enciende",
            description="Mi Laptop Pro 15 no enciende despues de una actualizacion de Windows. El LED de carga parpadea pero no arranca.",
            status="open",
            priority="high",
            created_at=datetime.utcnow() - timedelta(days=2),
        ),
        Ticket(
            customer_name="Maria Garcia",
            customer_email="maria@startup.io",
            subject="Monitor con lineas verticales",
            description="Mi monitor 4K muestra lineas verticales en la pantalla despues de 3 meses de uso. Todavia esta en garantia.",
            status="in_progress",
            priority="medium",
            created_at=datetime.utcnow() - timedelta(days=5),
        ),
        Ticket(
            customer_name="Juan Lopez",
            customer_email="juan@correo.com",
            subject="Consulta sobre envio",
            description="Hice un pedido hace 3 dias y aun no recibo numero de tracking. Cuando llegara mi pedido?",
            status="resolved",
            priority="low",
            created_at=datetime.utcnow() - timedelta(days=3),
        ),
    ]

    db.add_all(tickets)
    print(f"  - {len(tickets)} tickets created")

    # === CONVERSATIONS ===
    conversations = [
        Conversation(
            session_id="session-demo-001",
            role="user",
            content="Hola, busco una laptop para trabajar",
            created_at=datetime.utcnow() - timedelta(hours=2),
        ),
        Conversation(
            session_id="session-demo-001",
            role="assistant",
            content="Hola! Tenemos la Laptop Pro 15 con procesador Intel i7, 16GB RAM y 512GB SSD por $1,299.99. Es ideal para trabajo profesional. Te interesa?",
            metadata_={"products_shown": ["Laptop Pro 15"]},
            created_at=datetime.utcnow() - timedelta(hours=2, minutes=1),
        ),
        Conversation(
            session_id="session-demo-001",
            role="user",
            content="Si, me interesa. Tienen envio gratis?",
            created_at=datetime.utcnow() - timedelta(hours=2, minutes=2),
        ),
        Conversation(
            session_id="session-demo-002",
            role="user",
            content="Quiero hacer un pedido de 2 monitores",
            created_at=datetime.utcnow() - timedelta(hours=1),
        ),
        Conversation(
            session_id="session-demo-002",
            role="assistant",
            content="Perfecto! Tenemos el Monitor 27\" 4K por $449.99 c/u. Son $899.98 en total. Para proceder necesito tu nombre y email.",
            metadata_={"products_shown": ["Monitor 27 4K"]},
            created_at=datetime.utcnow() - timedelta(hours=1, minutes=1),
        ),
    ]

    db.add_all(conversations)
    print(f"  - {len(conversations)} conversation messages created")

    db.commit()
    db.close()
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_database()
