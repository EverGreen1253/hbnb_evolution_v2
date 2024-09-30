""" Amenity model """

from app.persistence import Base
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.place import place_amenity


class Amenity(Base):
    """ Amenity class """
    __tablename__ = 'amenities'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
    _name = Column("name", String(50), nullable=False)
    places_r = relationship("Place", secondary=place_amenity, back_populates = 'amenities_r')

    def __init__(self, name):
        if name is None:
            raise ValueError("Required attributes not specified!")

        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.name = name

    # --- Getters and Setters ---
    @property
    def name(self):
        """ Returns value of property name """
        return self._name

    @name.setter
    def name(self, value):
        """Setter for prop name"""
        # ensure that the value is up to 50 characters after removing excess white-space
        is_valid_name = 0 < len(value.strip()) <= 50
        if is_valid_name:
            self._name = value.strip()
        else:
            raise ValueError("Invalid name length!")


    # --- Methods ---
    def save(self):
        """Update the updated_at timestamp whenever the object is modified"""
        self.updated_at = datetime.now()
