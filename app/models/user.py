from sqlalchemy import Column, Integer, String
from app.database import Base, engine
from app.models.conversation import Conversation
from app.models.session import Session as SessionModel

# 数据库模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="user")

Base.metadata.create_all(bind=engine)
Conversation.metadata.create_all(bind=engine)
SessionModel.metadata.create_all(bind=engine)