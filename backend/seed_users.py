import sys
sys.path.insert(0, '/root/chatbot-empresarial/backend')
from database import SessionLocal, engine, Base
from app.models.user import User
from app.services.auth_service import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

admin = User(username='admin', password_hash=hash_password('Admin123!'), role='admin')
client = User(username='heladeria', password_hash=hash_password('Helado2026!'), role='client')
db.add(admin)
db.add(client)
db.commit()
print('Users seeded: admin + heladeria')
db.close()

