from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    filename = Column(String)
    file_path = Column(String)
    status = Column(String, default="processing")  # processing/ready/failed
    created_at = Column(DateTime, default=datetime.now)