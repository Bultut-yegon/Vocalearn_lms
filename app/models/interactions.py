from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.session import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    content_id = Column(Integer, ForeignKey("content_items.id"))
    event_type = Column(String(50))
    event_value = Column(Float, default=1.0)
