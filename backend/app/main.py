from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from app.core.auth import get_password_hash
from app.core.database import create_db_and_tables, engine
from app.models.models import User
from app.routers import auth, boards, lists, cards, labels

app = FastAPI(title="Trello Local API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
        "http://frontend:5173",  # Para Docker
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        admin_exists = session.exec(select(User).where(User.is_admin == True)).first()
        if not admin_exists:
            admin_user = session.exec(select(User).where(User.username == "admin")).first()
            if admin_user:
                admin_user.is_admin = True
                session.add(admin_user)
            else:
                admin_user = User(
                    username="admin",
                    password_hash=get_password_hash("changeme"),
                    is_admin=True,
                )
                session.add(admin_user)
            session.commit()

app.include_router(auth.router)
app.include_router(boards.router)
app.include_router(lists.router)
app.include_router(cards.router)
app.include_router(labels.router)

@app.get("/")
def root():
    return {"status": "ok"}
