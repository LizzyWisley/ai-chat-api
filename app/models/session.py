# Warning:Let you always trust youself.
# lesson:vipPython
# user:April 
# starting time:2026/5/19 16:45
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="新对话")
    created_at = Column(DateTime, default=func.now())