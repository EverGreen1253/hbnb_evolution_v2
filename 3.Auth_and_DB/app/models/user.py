""" User model """

from app.persistence import Base
import uuid
import re
from datetime import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship

bcrypt = Bcrypt()

class User(Base):
    """ User class """
    __tablename__ = 'users'

    # Remember: if you have getters & setters for any of the attributes
    # you can't use the same name for the attributes themselves

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
    _first_name = Column("first_name", String(50), nullable=False)
    _last_name = Column("last_name", String(50), nullable=False)
    _email = Column("email", String(120), nullable=False, unique=True)
    _password = Column("password", String(128), nullable=False)
    _is_admin = Column("is_admin", Boolean, default=False)
    reviews_r = relationship("Review", back_populates="user_r", cascade="delete, delete-orphan")
    properties_r = relationship("Place", back_populates="owner_r", cascade="delete, delete-orphan")

    def __init__(self, first_name, last_name, email, password=None, is_admin = False):
        # NOTE: Attributes that don't already exist will be
        # created when called in the constructor

        if first_name is None or last_name is None or email is None:
            raise ValueError("Required attributes not specified!")

        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.places = [] # List to store user-owned places
        self.reviews = [] # List to store user-written reviews

        # The method will call the setter
        self.hash_password(password)

    # --- Getters and Setters ---
    # Setters are actually called when values are assigned in the constructor!

    @property
    def first_name(self):
        """Getter for prop first_name"""
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        """Setter for prop first_name"""
        # ensure that the value is up to 50 alphabets only after removing excess white-space
        is_valid_name = 0 < len(value.strip()) <= 50
        if is_valid_name:
            self._first_name = value.strip()
        else:
            raise ValueError("Invalid first_name length!")

    @property
    def last_name(self):
        """Getter for prop last_name"""
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        """Setter for prop last_name"""
        # ensure that the value is up to 50 alphabets only after removing excess white-space
        is_valid_name = 0 < len(value.strip()) <= 50
        if is_valid_name:
            self._last_name = value.strip()
        else:
            raise ValueError("Invalid last_name length!")

    @property
    def email(self):
        """Getter for prop email"""
        return self._email

    @email.setter
    def email(self, value):
        """Setter for prop email"""
        # calls the method in the facade object
        from app.services import facade

        # add a simple regex check for email format. Nothing too fancy.
        is_valid_email = len(value.strip()) > 0 and re.search("^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", value)
        email_exists = facade.get_user_by_email(value.strip())
        if is_valid_email and not email_exists:
            self._email = value
        else:
            if email_exists:
                raise ValueError("Email already exists!")

            raise ValueError("Invalid email format!")

    @property
    def password(self):
        """Getter for prop password"""
        return self._password

    @password.setter
    def password(self, value):
        """Setter for prop password"""
        # The value passed in here is already hashed.
        # TODO: Modify hash_password to give a return value so we 
        # could do the assignment here instead of in the constructor?
        self._password = value

    @property
    def is_admin(self):
        """Getter for prop is_admin"""
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        """Setter for prop is_admin"""
        if isinstance(value, bool):
            self._is_admin = value
        else:
            raise ValueError("Invalid is_admin value!")


    # --- Methods ---
    def save(self):
        """Update the updated_at timestamp whenever the object is modified"""
        self.updated_at = datetime.now()

    def add_place(self, place):
        """Add a place to the user."""
        self.places.append(place)

    def add_review(self, review):
        """Add a review to the user."""
        self.reviews.append(review)

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def email_exists(email):
        """ Search through all Users to check the email exists """
        # Unused - the facade method get_user_by_email will handle this

    @staticmethod
    def user_exists(user_id):
        """ Search through all Users to ensure the specified user_id exists """
        # Unused - the facade method get_user will handle this
