from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel


# ── Label ────────────────────────────────────────────────────
class LabelCreate(BaseModel):
    name: str
    color: str = "#10B981"

class LabelRead(BaseModel):
    id: str
    name: str
    color: str
    class Config: from_attributes = True


# ── ChecklistItem ────────────────────────────────────────────
class ChecklistItemCreate(BaseModel):
    text: str
    position: int = 0

class ChecklistItemUpdate(BaseModel):
    text: Optional[str] = None
    done: Optional[bool] = None
    position: Optional[int] = None

class ChecklistItemRead(BaseModel):
    id: str
    text: str
    done: bool
    position: int
    class Config: from_attributes = True


# ── Card ─────────────────────────────────────────────────────
class CardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    position: int = 0
    due_date: Optional[date] = None
    list_id: str

class CardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    position: Optional[int] = None
    due_date: Optional[date] = None
    list_id: Optional[str] = None

class CardRead(BaseModel):
    id: str
    title: str
    description: Optional[str]
    position: int
    due_date: Optional[date]
    list_id: str
    created_at: datetime
    checklist_items: List[ChecklistItemRead] = []
    labels: List[LabelRead] = []
    class Config: from_attributes = True


# ── User / Auth ──────────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class UserAuth(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: str
    username: str
    is_admin: bool
    created_at: datetime
    class Config: from_attributes = True

class UserUpdate(BaseModel):
    is_admin: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None


# ── BoardList ────────────────────────────────────────────────
class BoardListCreate(BaseModel):
    title: str
    position: int = 0
    board_id: str

class BoardListUpdate(BaseModel):
    title: Optional[str] = None
    position: Optional[int] = None

class BoardListRead(BaseModel):
    id: str
    title: str
    position: int
    board_id: str
    cards: List[CardRead] = []
    class Config: from_attributes = True


# ── Board ────────────────────────────────────────────────────
class BoardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    color: str = "#3B82F6"
    sprint_end_date: Optional[date] = None
    position: Optional[int] = None

class BoardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    sprint_end_date: Optional[date] = None
    position: Optional[int] = None

class BoardRead(BaseModel):
    id: str
    title: str
    description: Optional[str]
    color: str
    sprint_end_date: Optional[date]
    position: int
    created_at: datetime
    lists: List[BoardListRead] = []
    class Config: from_attributes = True

class BoardSummary(BaseModel):
    id: str
    title: str
    description: Optional[str]
    color: str
    sprint_end_date: Optional[date]
    position: int
    created_at: datetime
    class Config: from_attributes = True
