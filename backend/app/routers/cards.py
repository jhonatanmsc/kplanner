from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.auth import get_current_user
from app.core.database import get_session
from app.models.models import Board, BoardList, Card, ChecklistItem, CardLabel, Label, User
from app.schemas.schemas import (
    CardCreate, CardUpdate, CardRead,
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemRead
)

router = APIRouter(prefix="/cards", tags=["cards"])


def _verify_board_owner(board_id: str, session: Session, current_user: User) -> Board:
    board = session.get(Board, board_id)
    if not board or board.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


def _verify_card_owner(card: Card, session: Session, current_user: User) -> None:
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    lst = session.get(BoardList, card.list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="Card not found")
    _verify_board_owner(lst.board_id, session, current_user)


@router.get("/", response_model=List[CardRead])
def list_cards(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[CardRead]:
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    board_ids = session.exec(select(Board.id).where(Board.owner_id == current_user.id)).all()
    if not board_ids:
        return []
    list_ids = session.exec(select(BoardList.id).where(BoardList.board_id.in_(board_ids))).all()
    if not list_ids:
        return []
    cards = session.exec(select(Card).where(Card.list_id.in_(list_ids)).order_by(Card.position)).all()
    return [_load_card(card, session) for card in cards]


def _load_card(card: Card, session: Session):
    checklist_items = session.exec(
        select(ChecklistItem).where(ChecklistItem.card_id == card.id).order_by(ChecklistItem.position)
    ).all()
    card_label_rows = session.exec(select(CardLabel).where(CardLabel.card_id == card.id)).all()
    labels = [session.get(Label, cl.label_id) for cl in card_label_rows]
    card_dict = card.model_dump()
    card_dict['checklist_items'] = checklist_items
    card_dict['labels'] = labels
    return card_dict


@router.post("/", response_model=CardRead)
def create_card(
    data: CardCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    lst = session.get(BoardList, data.list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    _verify_board_owner(lst.board_id, session, current_user)
    card = Card(**data.model_dump())
    session.add(card)
    session.commit()
    session.refresh(card)
    return _load_card(card, session)


@router.get("/{card_id}", response_model=CardRead)
def get_card(
    card_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    card = session.get(Card, card_id)
    _verify_card_owner(card, session, current_user)
    return _load_card(card, session)


@router.patch("/{card_id}", response_model=CardRead)
def update_card(
    card_id: str,
    data: CardUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    card = session.get(Card, card_id)
    _verify_card_owner(card, session, current_user)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(card, k, v)
    session.commit()
    session.refresh(card)
    return _load_card(card, session)


@router.delete("/{card_id}")
def delete_card(
    card_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    card = session.get(Card, card_id)
    _verify_card_owner(card, session, current_user)
    session.delete(card)
    session.commit()
    return {"ok": True}


# ── Checklist ────────────────────────────────────────────────
@router.post("/{card_id}/checklist", response_model=ChecklistItemRead)
def add_checklist_item(
    card_id: str,
    data: ChecklistItemCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    card = session.get(Card, card_id)
    _verify_card_owner(card, session, current_user)
    item = ChecklistItem(card_id=card_id, **data.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.patch("/{card_id}/checklist/{item_id}", response_model=ChecklistItemRead)
def update_checklist_item(
    card_id: str,
    item_id: str,
    data: ChecklistItemUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    item = session.get(ChecklistItem, item_id)
    if not item or item.card_id != card_id:
        raise HTTPException(status_code=404, detail="Item not found")
    card = session.get(Card, card_id)
    _verify_card_owner(card, session, current_user)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{card_id}/checklist/{item_id}")
def delete_checklist_item(
    card_id: str,
    item_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    item = session.get(ChecklistItem, item_id)
    if not item or item.card_id != card_id:
        raise HTTPException(status_code=404, detail="Item not found")
    card = session.get(Card, card_id)
    _verify_card_owner(card, session, current_user)
    session.delete(item)
    session.commit()
    return {"ok": True}


# ── Labels ───────────────────────────────────────────────────
@router.post("/{card_id}/labels/{label_id}")
def add_label(
    card_id: str,
    label_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    card = session.get(Card, card_id)
    _verify_card_owner(card, session, current_user)
    existing = session.get(CardLabel, (card_id, label_id))
    if not existing:
        cl = CardLabel(card_id=card_id, label_id=label_id)
        session.add(cl)
        session.commit()
    return {"ok": True}


@router.delete("/{card_id}/labels/{label_id}")
def remove_label(
    card_id: str,
    label_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    card = session.get(Card, card_id)
    _verify_card_owner(card, session, current_user)
    cl = session.get(CardLabel, (card_id, label_id))
    if cl:
        session.delete(cl)
        session.commit()
    return {"ok": True}
