from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, oauth2_scheme,
    SECRET_KEY, ALGORITHM
)
router = APIRouter()
# 注册接口
@router.post("/register")
def register(user: UserCreate, db=Depends(get_db)):
    exist = db.query(User).filter(User.email == user.email).first()
    if exist:
        raise HTTPException(status_code=400, detail="邮箱已注册")
    hashed_pw = get_password_hash(user.password)
    new_user = User(email=user.email, username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"msg": "注册成功", "code": 200}

# 登录接口
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
#get
@router.get("/user/me")
def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        return {"email": user.email, "username": user.username}
    except JWTError:
        raise HTTPException(status_code=401, detail="无效凭证")