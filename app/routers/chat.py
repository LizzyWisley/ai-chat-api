from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import urllib.request
import json

from app.database import get_db
from app.models.conversation import Conversation
from app.core.security import oauth2_scheme, SECRET_KEY, ALGORITHM, DEEPSEEK_API_KEY
from pydantic import BaseModel

router = APIRouter()


class MessageRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: MessageRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")

    from app.models.user import User
    user = db.query(User).filter(User.email == email).first()

    # 先存用户消息
    user_msg = Conversation(user_id=user.id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    # 查询历史对话
    history = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).order_by(Conversation.id).all()

    # 构建带上下文的消息列表
    messages = [{"role": c.role, "content": c.content} for c in history]

    # 调用 DeepSeek API
    req_data = json.dumps({
        "model": "deepseek-chat",
        "messages": messages
    }).encode()

    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=req_data,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())

    reply = result["choices"][0]["message"]["content"]

    ai_msg = Conversation(user_id=user.id, role="assistant", content=reply)
    db.add(ai_msg)
    db.commit()

    return {"reply": reply}


@router.get("/chat/history")
def get_history(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")

    from app.models.user import User
    user = db.query(User).filter(User.email == email).first()

    history = db.query(Conversation).filter(Conversation.user_id == user.id).all()
    return [{"role": c.role, "content": c.content, "time": c.created_at} for c in history]