from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ParametroRuta(Base):
    __tablename__ = "waterproof_pr_parametro_ruta"
    __table_args__ = ({"schema": "public"})

    id_parametro_ruta = Column(Integer, primary_key = True)
    id_basin = Column(Integer)
    ruta = Column(String)
    id_parametro = Column(Integer)