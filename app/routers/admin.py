# Warning:Let you always trust youself.
# lesson:vipPython
# user:April 
# starting time:2026/5/17 19:49
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
from app.models.user import User
from app.core.security import oauth2_scheme, SECRET_KEY, ALGORITHM

router = APIRouter()

@router.get("/admin/users")
def get_all_users(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")

    # 查当前用户的角色
    current_user = db.query(User).filter(User.email == email).first()
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足，仅管理员可访问")

    # 返回所有用户
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "username": u.username, "role": u.role} for u in users]