from fastapi import FastAPI, HTTPException, Depends, status, Header
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from typing import Optional
from sqlalchemy.orm import Session

from database import (
    get_db,
    verify_password,
    User,
    get_user_by_username,
    create_user as db_create_user,
    ensure_schema,
    init_default_admin,
    SessionLocal
)

app = FastAPI(title="Auth API", version="1.0.0")

SECRET_KEY = "super_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 1

def create_access_token(username: str, role: str) -> tuple[str, int]:
    expires = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": expires
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, int(expires.timestamp())

class UserCreate(BaseModel):
    username: str
    password: str
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserResponse(BaseModel):
    username: str
    role: str

    class Config:
        from_attributes = True

class UserDetails(BaseModel):
    username: str
    role: str
    iat: int
    exp: int

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@app.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, credentials.username)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    token, exp = create_access_token(user.username, user.role)
    expires_in = int(exp - datetime.now(timezone.utc).timestamp())
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": expires_in
    }

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    new_user = db_create_user(
        db=db,
        username=user_data.username,
        password=user_data.password,
        role=user_data.role.lower() if user_data.role else "user"
    )
    
    return {
        "username": new_user.username,
        "role": new_user.role
    }

@app.get("/user_details", response_model=UserDetails)
def get_user_details(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "role": current_user.role,
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)).timestamp())
    }

@app.get("/")
def root():
    return {
        "message": "Auth API - System Uwierzytelniania",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "login": "POST /login",
            "users": "POST /users (admin only)",
            "user_details": "GET /user_details (requires token)"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.on_event("startup")
async def startup_event():
    ensure_schema()
    db = SessionLocal()
    try:
        init_default_admin(db)
    finally:
        db.close()
    print("Aplikacja uruchomiona!")
    print("Domyślne konto admin jest dostępne")
    print("Username: admin")
    print("Password: admin123")

if __name__ == "__main__":
    print("To run this app, use: python -m uvicorn main:app --reload")

