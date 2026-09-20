from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.services.auth_service import authenticate_user, create_access_token, get_current_user, create_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    token = create_access_token({"sub": user.username, "role": user.role})
    return LoginResponse(
        access_token=token,
        username=user.username,
        role=user.role
    )

@router.get("/me", response_model=UserResponse)
def get_me(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return UserResponse(id=user.id, username=user.username, role=user.role, is_active=user.is_active)

@router.post("/register", response_model=UserResponse)
def register(request: LoginRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de admin requerido")
    token = authorization.split(" ")[1]
    admin = get_current_user(token, db)
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Solo admins pueden crear usuarios")
    user = create_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    return UserResponse(id=user.id, username=user.username, role=user.role, is_active=user.is_active)

