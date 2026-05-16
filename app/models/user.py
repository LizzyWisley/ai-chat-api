from sqlalchemy import Column, Integer, String
from app.database import Base, engine
# 数据库模型
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)
from app.models.conversation import Conversation
Conversation.metadata.create_all(bind=engine)
