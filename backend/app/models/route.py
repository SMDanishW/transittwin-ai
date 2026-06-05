from sqlalchemy import Column, String

from app.database import Base


class Route(Base):
    __tablename__ = "routes"

    id = Column(String, primary_key=True)       # e.g. HSL:1007
    short_name = Column(String)                 # "7"
    long_name = Column(String)                  # "Töölö - Pasila"
    mode = Column(String)                       # BUS TRAM RAIL METRO FERRY
    color = Column(String)                      # hex without #
    agency_name = Column(String)
