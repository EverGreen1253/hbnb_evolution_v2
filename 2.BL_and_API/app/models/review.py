import uuid
from datetime import datetime
from models.user import User
from models.place import Place

class Review:
    def __init__(self, text, rating, place_id, user_id):
        if text is None or rating is None or place_id is None or user_id is None:
            raise ValueError("Required attributes not specified!")

        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.text = text
        self.rating = rating
        self.place_id = place_id # relationship - id of Place that the Review is for
        self.user_id = user_id # relationship - id of User who wrote the Review

    # --- Getters and Setters ---
    @property
    def text(self):
        """ Returns value of property text """
        return self._text

    @text.setter
    def text(self, value):
        """Setter for prop text"""
        # Can't think of any special checks to perform here tbh
        self._text = value

    @property
    def rating(self):
        """ Returns value of property rating """
        return self._rating

    @rating.setter
    def rating(self, value):
        """Setter for prop rating"""
        if isinstance(value, int) and 1 <= value <= 5:
            self._rating = value
        else:
            raise ValueError("Invalid value specified for rating")

    @property
    def user_id(self):
        """ Returns value of property user_id """
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        """Setter for prop user_id"""
        # Calls the static method in the User model
        user_exists = User.user_exists(value)
        if user_exists:
            self._user_id = value
        else:
            raise ValueError("Owner does not exist!")

    @property
    def place_id(self):
        """ Returns value of property place_id """
        return self._place_id

    @place_id.setter
    def place_id(self, value):
        """Setter for prop place_id"""
        # Calls the static method in the Place model
        place_exists = Place.place_exists(value)
        if place_exists:
            self._place_id = value
        else:
            raise ValueError("Place does not exist!")

    # --- Methods ---
    def save(self):
        """Update the updated_at timestamp whenever the object is modified"""
        self.updated_at = datetime.now()
