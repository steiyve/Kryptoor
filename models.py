from sqlalchemy import Boolean, Column, Integer, String
from database import Base
class PasswordDB(Base):
    __tablename__ = 'password'
    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String(50),unique=False)
    password = Column(String(500),unique=False)