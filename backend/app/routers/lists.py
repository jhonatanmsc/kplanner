from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.auth import get_current_user
from app.core.database import get_session
from app.models.models import Board, BoardList, Card, ChecklistItem, CardLabel, User
from app.schemas.schemas import BoardListCreate, BoardListUpdate, BoardListRead

router = APIRouter(prefix="/lists", tags=["lists"])


def _verify_board_owner(board_id: str, session: Session, current_user: User) -> Board:
    board = session.get(Board, board_id)
    if not board or board.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


def _load_list(lst: BoardList, session: Session) -> BoardList:
    cards = session.exec(
        select(Card).where(Card.list_id == lst.id).order_by(Card.position)
    ).all()
    for card in cards:
        card.checklist_items = session.exec(
            select(ChecklistItem).where(ChecklistItem.card_id == card.id).order_by(ChecklistItem.position)
        ).all()
        from app.models.models import Label
        card_label_rows = session.exec(select(CardLabel).where(CardLabel.card_id == card.id)).all()
        card.labels = [session.get(Label, cl.label_id) for cl in card_label_rows]
    lst.cards = cards
    return lst


@router.post("/", response_model=BoardListRead)
def create_list(
    data: BoardListCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    _verify_board_owner(data.board_id, session, current_user)
    lst = BoardList(**data.model_dump())
    session.add(lst)
    session.commit()
    session.refresh(lst)
    return _load_list(lst, session)


@router.patch("/{list_id}", response_model=BoardListRead)
def update_list(
    list_id: str,
    data: BoardListUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    lst = session.get(BoardList, list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    _verify_board_owner(lst.board_id, session, current_user)
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(lst, k, v)
    session.commit()
    session.refresh(lst)
    return _load_list(lst, session)


@router.delete("/{list_id}")
def delete_list(
    list_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    lst = session.get(BoardList, list_id)
    if not lst:
        raise HTTPException(status_code=404, detail="List not found")
    _verify_board_owner(lst.board_id, session, current_user)
    session.delete(lst)
    session.commit()
    return {"ok": True}
