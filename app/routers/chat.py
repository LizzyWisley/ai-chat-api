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

#用Agent
@router.post("/chat")
def chat(request: MessageRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")

    from app.models.user import User
    user = db.query(User).filter(User.email == email).first()

    # 校验session归属
    from app.models.session import Session as SessionModel
    session = db.query(SessionModel).filter(
        SessionModel.id == request.session_id,
        SessionModel.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(status_code=403, detail="无权访问此会话")

    # 存用户消息
    user_msg = Conversation(user_id=user.id, session_id=request.session_id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()

    # 自动生成标题
    msg_count = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.session_id == request.session_id
    ).count()

    if msg_count == 1:
        import urllib.request
        import json as json_lib
        title_req_data = json_lib.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": f"请用5个字以内概括这句话的主题，只返回标题不要其他内容：{request.message}"}]
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
            title_result = json_lib.loads(title_resp.read())
        title = title_result["choices"][0]["message"]["content"]
        session.title = title
        db.commit()

    # 用 Agent 回复
    # 用 Agent 回复
    try:
        from app.core.agent import create_agent
        agent = create_agent(db, user.id, request.session_id)
        result = agent.invoke({"messages": [{"role": "user", "content": request.message}]})
        reply = result["messages"][-1].content
    except Exception as e:
        print(f"Agent 调用失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI 回复生成失败: {str(e)}")

    # 存AI回复
    ai_msg = Conversation(user_id=user.id, session_id=request.session_id, role="assistant", content=reply)
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