from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.core.auth import get_current_user
from app.core.database import get_session
from app.models.models import Board, BoardList, User
from app.schemas.schemas import BoardCreate, BoardUpdate, BoardRead, BoardSummary

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("/", response_model=list[BoardSummary])
def list_boards(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session.exec(
        select(Board)
        .where(Board.owner_id == current_user.id)
        .order_by(Board.position, Board.created_at.desc())
    ).all()


@router.post("/", response_model=BoardSummary)
def create_board(data: BoardCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = data.model_dump(exclude_none=True)
    if payload.get('position') is None:
        max_position = session.exec(select(func.max(Board.position))).one() or 0
        payload['position'] = max_position + 20
    board = Board(**payload, owner_id=current_user.id)
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


@router.get("/{board_id}", response_model=BoardRead)
def get_board(board_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    board = session.get(Board, board_id)
    if not board or board.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    lists = session.exec(
        select(BoardList).where(BoardList.board_id == board_id).order_by(BoardList.position)
    ).all()
    board.lists = lists
    return board


@router.patch("/{board_id}", response_model=BoardSummary)
def update_board(board_id: str, data: BoardUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    board = session.get(Board, board_id)
    if not board or board.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(board, k, v)
    session.commit()
    session.refresh(board)
    return board


@router.delete("/{board_id}")
def delete_board(board_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    board = session.get(Board, board_id)
    if not board or board.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Board not found")
    session.delete(board)
    session.commit()
    return {"ok": True}
