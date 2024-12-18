"""
Models for Customer

All of the models are stored in this module
"""

import logging
from flask_sqlalchemy import SQLAlchemy
from flask import current_app as app

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""


class Customer(db.Model):
    """
    Class that represents a Customer
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    password = db.Column(db.String(63), nullable=False)
    email = db.Column(db.String(63), nullable=False)
    address = db.Column(db.String(63), nullable=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return f"<Customer {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Customer to the database
        """
        app.logger.info("Creating %s, %s, %s", self.name, self.email, self.password)

        self.id = None  # pylint: disable=invalid-name
        if self.name is None:
            raise DataValidationError("name attribute is not set")
        if not self.name.strip():
            raise DataValidationError("name attribute is not set")
        if self.email is None:
            raise DataValidationError("email attribute is not set")
        if not self.email.strip():
            raise DataValidationError("email attribute is not set")
        if self.password is None:
            raise DataValidationError("password attribute is not set")
        if not self.password.strip():
            raise DataValidationError("password attribute is not set")

        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Customer to the database
        """
        if not self.id:
            raise DataValidationError("Customer ID cannot be None")
        logger.info("Saving %s", self.name)
        if not self.name.strip():
            raise DataValidationError("name attribute is not set")
        if not self.email.strip():
            raise DataValidationError("email attribute is not set")
        if not self.password.strip():
            raise DataValidationError("password attribute is not set")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Customer from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Customer into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "password": self.password,
            "email": self.email,
            "address": self.address,
            "active": self.active,
        }

    def deserialize(self, data):
        """
        Deserializes a Customer from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        # id might not be present on create customer
        app.logger.info("deserialize(%s)", data)
        try:
            self.name = data["name"]
            self.email = data["email"]
            if isinstance(data["active"], bool):
                self.active = data["active"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [active]: " + str(type(data["active"]))
                )
            self.address = data["address"]
            self.password = data["password"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid customer: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data"
            ) from error

        # if there is no id and the data has one, assign it
        if not self.id and "id" in data:
            self.id = data["id"]

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Customers in the database"""
        logger.info("Processing all Customers")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Customer by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Customers with the given name

        Args:
            name (string): the name of the Customers you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_active(cls, active):
        """Returns all Customers with the given active status

        Args:
            active (bool): the active status of the Customers you want to match
        """
        logger.info("Processing active query for %s ...", active)
        return cls.query.filter(cls.active == active)

    @classmethod
    def find_by_address(cls, address):
        """Returns all Customers with the given address

        Args:
            address (string): the address of the Customers you want to match
        """
        logger.info("Processing address query for %s ...", address)
        return cls.query.filter(cls.address == address)

    @classmethod
    def find_by_email(cls, email):
        """Returns all Customers with the given email

        Args:
            email (string): the email of the Customers you want to match
        """
        logger.info("Processing email query for %s ...", email)
        return cls.query.filter(cls.email == email)
