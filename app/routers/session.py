# Warning:Let you always trust youself.
# lesson:vipPython
# user:April 
# starting time:2026/5/19 16:47
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
from app.models.session import Session as SessionModel
from app.models.conversation import Conversation
from app.core.security import oauth2_scheme, SECRET_KEY, ALGORITHM
from app.models.user import User

router = APIRouter()
# 新建会话
@router.post("/sessions")
def create_session(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")

    user = db.query(User).filter(User.email == email).first()
    new_session = SessionModel(user_id=user.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {"session_id": new_session.id, "title": new_session.title}


# 查询当前用户所有会话
@router.get("/sessions")
def get_sessions(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")

    user = db.query(User).filter(User.email == email).first()
    sessions = db.query(SessionModel).filter(SessionModel.user_id == user.id).all()
    return [{"session_id": s.id, "title": s.title, "created_at": s.created_at} for s in sessions]


@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")

    user = db.query(User).filter(User.email == email).first()

    messages = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.session_id == session_id
    ).order_by(Conversation.id).all()

    return [{"role": m.role, "content": m.content, "time": m.created_at} for m in messages]