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
    session_id: int

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
    user_msg = Conversation(user_id=user.id, session_id=request.session_id,role="user", content=request.message)
    db.add(user_msg)
    db.commit()
    # 功能10：如果是第一条消息，自动生成会话标题
    msg_count = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.session_id == request.session_id
    ).count()

    if msg_count == 1:  # 刚存入的这条是第一条
        title_req_data = json.dumps({
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": f"请用5个字以内概括这句话的主题，只返回标题不要其他内容：{request.message}"}]
        }).encode()

        title_req = urllib.request.Request(
            "https://api.deepseek.com/chat/completions",
            data=title_req_data,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(title_req, timeout=30) as title_resp:
            title_result = json.loads(title_resp.read())

        title = title_result["choices"][0]["message"]["content"]

        from app.models.session import Session as SessionModel
        session = db.query(SessionModel).filter(SessionModel.id == request.session_id).first()
        session.title = title
        db.commit()


    # 查询历史对话
    history = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.session_id == request.session_id
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

    ai_msg = Conversation(user_id=user.id, session_id=request.session_id,role="assistant", content=reply)
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