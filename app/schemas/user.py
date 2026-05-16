from pydantic import BaseModel
# 请求模型
class UserCreate(BaseModel):
    email: str
    username: str
    password: str