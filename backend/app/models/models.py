from typing import Optional, List
from datetime import datetime, date
from sqlmodel import SQLModel, Field, Relationship
import uuid


def gen_uuid() -> str:
    return str(uuid.uuid4())


# ── User ─────────────────────────────────────────────────────
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=gen_uuid, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    boards: List["Board"] = Relationship(back_populates="owner")


# ── Board ────────────────────────────────────────────────────
class Board(SQLModel, table=True):
    __tablename__ = "boards"

    id: str = Field(default_factory=gen_uuid, primary_key=True)
    title: str
    description: Optional[str] = None
    color: str = Field(default="#3B82F6")
    sprint_end_date: Optional[date] = None
    position: int = Field(default=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: str = Field(foreign_key="users.id")

    owner: Optional[User] = Relationship(back_populates="boards")
    lists: List["BoardList"] = Relationship(back_populates="board", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


# ── BoardList ────────────────────────────────────────────────
class BoardList(SQLModel, table=True):
    __tablename__ = "board_lists"

    id: str = Field(default_factory=gen_uuid, primary_key=True)
    title: str
    position: int = Field(default=0)
    board_id: str = Field(foreign_key="boards.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    board: Optional[Board] = Relationship(back_populates="lists")
    cards: List["Card"] = Relationship(back_populates="list", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


# ── Label ────────────────────────────────────────────────────
class Label(SQLModel, table=True):
    __tablename__ = "labels"

    id: str = Field(default_factory=gen_uuid, primary_key=True)
    name: str
    color: str = Field(default="#10B981")

    card_labels: List["CardLabel"] = Relationship(back_populates="label", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


# ── Card ─────────────────────────────────────────────────────
class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: str = Field(default_factory=gen_uuid, primary_key=True)
    title: str
    description: Optional[str] = None
    position: int = Field(default=0)
    due_date: Optional[date] = None
    list_id: str = Field(foreign_key="board_lists.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    list: Optional[BoardList] = Relationship(back_populates="cards")
    checklist_items: List["ChecklistItem"] = Relationship(back_populates="card", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    card_labels: List["CardLabel"] = Relationship(back_populates="card", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


# ── ChecklistItem ────────────────────────────────────────────
class ChecklistItem(SQLModel, table=True):
    __tablename__ = "checklist_items"

    id: str = Field(default_factory=gen_uuid, primary_key=True)
    text: str
    done: bool = Field(default=False)
    position: int = Field(default=0)
    card_id: str = Field(foreign_key="cards.id")

    card: Optional[Card] = Relationship(back_populates="checklist_items")


# ── CardLabel (pivot) ────────────────────────────────────────
class CardLabel(SQLModel, table=True):
    __tablename__ = "card_labels"

    card_id: str = Field(foreign_key="cards.id", primary_key=True)
    label_id: str = Field(foreign_key="labels.id", primary_key=True)

    card: Optional[Card] = Relationship(back_populates="card_labels")
    label: Optional[Label] = Relationship(back_populates="card_labels")
