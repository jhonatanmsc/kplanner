from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.models import Label
from app.schemas.schemas import LabelCreate, LabelRead

router = APIRouter(prefix="/labels", tags=["labels"])


@router.get("/", response_model=list[LabelRead])
def list_labels(session: Session = Depends(get_session)):
    return session.exec(select(Label)).all()


@router.post("/", response_model=LabelRead)
def create_label(data: LabelCreate, session: Session = Depends(get_session)):
    label = Label(**data.model_dump())
    session.add(label)
    session.commit()
    session.refresh(label)
    return label


@router.delete("/{label_id}")
def delete_label(label_id: str, session: Session = Depends(get_session)):
    label = session.get(Label, label_id)
    if not label:
        raise HTTPException(status_code=404, detail="Label not found")
    session.delete(label)
    session.commit()
    return {"ok": True}
