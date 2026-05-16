from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
import bcrypt
import os
# 基础配置
SECRET_KEY = os.environ.get("SECRET_KEY", "test-key-123456")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户信息接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
