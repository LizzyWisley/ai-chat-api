# Warning:Let you always trust youself.
# lesson:vipPython
# user:April 
# starting time:2026/5/15 17:21
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)      # "user" 或 "assistant"
    content = Column(String)   # 消息内容
    created_at = Column(DateTime, default=func.now())