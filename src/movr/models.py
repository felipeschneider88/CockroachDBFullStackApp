"""
Aligns sqlalchemy's schema for the "vehicles" table with the database.
"""

from sqlalchemy import (Boolean, Column, DateTime, Float, Integer,
                        PrimaryKeyConstraint, String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func

Base = declarative_base()


class Vehicle(Base):
    """
    DeclarativeMeta class for the vehicles table.

    Arguments:
        Base {DeclarativeMeta} -- Base class for model to inherit.
    """
    __tablename__ = 'vehicles'
    id = Column(UUID)
    last_longitude = Column(Float)
    last_latitude = Column(Float)
    last_checkin = Column(DateTime, default=func.now)
    in_use = Column(Boolean)
    vehicle_type = Column(String)
    battery = Column(Integer)
    PrimaryKeyConstraint(id)

    def __repr__(self):
        return "<Vehicle(id='{0}', vehicle_type='{1}')>".format(
            self.id, self.vehicle_type)
