from sqlalchemy import Column, Integer, String, Text
from app.db.session import Base

class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True)
    title = Column(String(255))
    description = Column(Text)
    tags = Column(String(255))
