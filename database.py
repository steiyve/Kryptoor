from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from variable import dbpassword

URL_DATABASE = 'mysql+pymysql://root:'+dbpassword+'@localhost:3306/kryptoor'

engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()