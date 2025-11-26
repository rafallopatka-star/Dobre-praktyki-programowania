import bcrypt
from sqlalchemy import create_engine, Column, String, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DATABASE_URL = "sqlite:///./auth.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")

EXPECTED_COLUMNS = {"username", "hashed_password", "role"}


def ensure_schema() -> None:
    # Recreate table when legacy schemas with extra columns are detected
    inspector = inspect(engine)
    if "users" in inspector.get_table_names():
        existing_columns = {col["name"] for col in inspector.get_columns("users")}
        if existing_columns != EXPECTED_COLUMNS:
            with engine.begin() as connection:
                User.__table__.drop(connection, checkfirst=True)
                User.__table__.create(connection)
            return
    Base.metadata.create_all(bind=engine, checkfirst=True)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str, role: str = "user") -> User:
    hashed_pw = hash_password(password)
    db_user = User(
        username=username,
        hashed_password=hashed_pw,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def init_default_admin(db: Session):
    admin = get_user_by_username(db, "admin")
    if not admin:
        create_user(
            db=db,
            username="admin",
            password="admin123",
            role="admin"
        )
        print(" Utworzono domyślne konto administratora")


