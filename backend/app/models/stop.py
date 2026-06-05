from geoalchemy2 import Geometry
from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class Stop(Base):
    __tablename__ = "stops"

    id = Column(String, primary_key=True)       # e.g. HSL:1234567
    name = Column(String, nullable=False)
    code = Column(String)                        # short display code
    vehicle_type = Column(Integer)               # 0=tram 1=metro 2=rail 3=bus 4=ferry
    platform_code = Column(String)
    zone_id = Column(String)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
