from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from aether.database.connection import Base

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String(50))
    module = Column(String(100))
    message = Column(Text)

class CognitiveMemory(Base):
    __tablename__ = "cognitive_memory"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True)
    value = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
