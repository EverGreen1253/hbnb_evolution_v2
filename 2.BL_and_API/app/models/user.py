""" User model """

import uuid
import re
from datetime import datetime

class User:
    """ User class """
    # NOTE: The attribute declarations below can be considered redundant
    # but I still like to do it out of habit.

    # id = None
    # first_name = ""
    # last_name = ""
    # email = ""
    # is_admin = False
    # created_at = None
    # updated_at = None
    # places = []
    # reviews = []

    def __init__(self, first_name, last_name, email, is_admin = False):
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
        """Setter for prop last_name"""
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

    @staticmethod
    def email_exists(email):
        """ Search through all Users to check the email exists """
        # Unused - the facade method get_user_by_email will handle this

    @staticmethod
    def user_exists(user_id):
        """ Search through all Users to ensure the specified user_id exists """
        # Unused - the facade method get_user will handle this
