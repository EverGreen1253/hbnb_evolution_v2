""" Place model """

from app.persistence import Base
import uuid
from datetime import datetime
from app.models.user import User
from sqlalchemy import Column, String, Float, Text, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship

# define the many-to-many table
place_amenity = Table(
    'place_amenity',
    Base.metadata,
    Column('place_id', String(60), ForeignKey('places.id'), primary_key=True),
    Column('amenity_id', String(60), ForeignKey('amenities.id'), primary_key=True)
)

class Place(Base):
    """ Place class """
    __tablename__ = 'places'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
    _title = Column("title", String(100), nullable=False)
    _description = Column("description", Text, nullable=False)
    _price = Column("price", Float, nullable=False)
    _latitude = Column("latitude", Float, nullable=False)
    _longitude = Column("longitude", Float, nullable=False)
    _owner_id = Column("owner_id", String(60), ForeignKey('users.id'), nullable=False)
    amenities_r = relationship("Amenity", secondary=place_amenity, back_populates = 'places_r')
    reviews_r = relationship("Review", back_populates="place_r")
    owner_r = relationship("User", back_populates="properties_r")

    def __init__(self, title, description, price, latitude, longitude, owner_id):
        if title is None or description is None or price is None or latitude is None or longitude is None or owner_id is None:
            raise ValueError("Required attributes not specified!")

        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id
        self.reviews = []  # relationship - List to store related reviews
        self.amenities = []  # relationship - List to store related amenities

    # --- Getters and Setters ---
    @property
    def title(self):
        """ Returns value of property title """
        return self._title

    @title.setter
    def title(self, value):
        """Setter for prop title"""
        # ensure that the value is up to 100 alphabets only after removing excess white-space
        is_valid_title = 0 < len(value.strip()) <= 100
        if is_valid_title:
            self._title = value.strip()
        else:
            raise ValueError("Invalid title length!")

    @property
    def description(self):
        """ Returns value of property description """
        return self._description

    @description.setter
    def description(self, value):
        """Setter for prop description"""
        # Can't think of any special checks to perform here tbh
        self._description = value

    @property
    def price(self):
        """ Returns value of property price """
        return self._price

    @price.setter
    def price(self, value):
        """Setter for prop price"""
        if isinstance(value, float) and value > 0.0:
            self._price = value
        else:
            raise ValueError("Invalid value specified for price")

    @property
    def latitude(self):
        """ Returns value of property latitude """
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        """Setter for prop latitude"""
        if isinstance(value, float) and -90.0 <= value <= 90.0:
            self._latitude = value
        else:
            raise ValueError("Invalid value specified for Latitude")

    @property
    def longitude(self):
        """ Returns value of property longitude """
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        """Setter for prop longitude"""
        if isinstance(value, float) and -180.0 <= value <= 180.0:
            self._longitude = value
        else:
            raise ValueError("Invalid value specified for Longitude")

    @property
    def owner_id(self):
        """ Returns value of property owner """
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value):
        """Setter for prop owner"""
        self._owner_id = value

    # --- Methods ---
    def save(self):
        """Update the updated_at timestamp whenever the object is modified"""
        self.updated_at = datetime.now()

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)

    @staticmethod
    def place_exists(place_id):
        """ Search through all Places to ensure the specified place_id exists """
        # Unused - the facade get_place method will handle this
