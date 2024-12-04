######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Customer Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customer
"""
from functools import wraps
from flask import abort, request
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Customer
from service.common import status  # HTTP Status Codes

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Customer Demo REST API Service",
    description="This is a sample server Customer store server.",
    default="customers",
    default_label="Customer operations",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# API Model Definition
######################################################################
# Define the API model for Customer Creation
create_model = api.model(
    "Customer",
    {
        "id": fields.Integer(
            description="A list of Customer IDs associated with the customer, stored as a JSON array.",
            example=["customer_id_1", "customer_id_2"],
            required=True,
        ),
        "name": fields.String(
            required=True,
            description="The name of the customer.",
            example="Wang",
        ),
        "password": fields.String(
            required=True,
            description="The password of of the customer.",
            example="123456",
        ),
        "email": fields.String(
            required=True,
            description="The email of of the customer.",
            example="123456@nyu.edu",
        ),
        "address": fields.String(
            required=False,
            description="The address of of the customer.",
            example="apt101",
        ),
        "active": fields.Boolean(
            required=True,
            description="A boolean indicating whether the customer is active.",
        ),
    },
)

# Define the API model for Customer
customer_model = api.inherit(
    "CustomerModel",
    create_model,
    {
        "id": fields.String(
            description="A unique identifier for the customer, generated automatically as a UUID.",
            readOnly=True,
        ),
        "created_at": fields.DateTime(
            readOnly=True,
            description="The timestamp when the customer was created.",
            dt_format="iso8601",
        ),
        "updated_at": fields.DateTime(
            readOnly=True,
            description="The timestamp when the customer was last updated.",
            dt_format="iso8601",
        ),
    },
)


######################################################################
# Setup the request parser for customers
######################################################################
args_config = [
    ("name", str, "args", True, "Filter customers by name"),
    ("id", str, "args", True, "Filter customers by customer ID"),
    (
        "active",
        inputs.boolean,
        "args",
        True,
        "Filter customers by active status",
    ),
]


# Init customer args
customer_args = reqparse.RequestParser()

for arg_name, arg_type, location, required, help_text in args_config:
    customer_args.add_argument(
        arg_name, type=arg_type, location=location, required=required, help=help_text
    )


######################################################################
# Content Type Check Decorator
######################################################################
def require_content_type(content_type):
    """Decorator to require a specific content type for this endpoint"""

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # Check if the Content-Type header matches the expected content type
            if request.headers.get("Content-Type", "") != content_type:
                app.logger.error(
                    "Invalid Content-Type: %s",
                    request.headers.get("Content-Type", "Content-Type not set"),
                )
                # If not, abort the request and return an error message
                abort(
                    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    f"Content-Type must be {content_type}",
                )
            return func(*args, **kwargs)

        return decorated_function

    return decorator


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# FLASK-RESTX APIs
######################################################################
@api.route("/customers/<uuid:customer_id>")
@api.param("customer_id", "The Customer identifier")
@api.response(404, "Customer not found")
class CustomerResource(Resource):
    """
    CustomerResource class

    Allows the manipulation of a single Customer
    GET /customer{id} - Returns a Customer with the id
    PUT /customer{id} - Update a Customer with the id
    DELETE /customer{id} -  Deletes a Customer with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("get_customer")
    @api.response(404, "Customer not found")
    @api.marshal_with(customer_model)
    def get(self, customer_id):
        """
        Retrieve a single Customer

        This endpoint will return a Customer based on it's id
        """
        app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)

        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("update_customer")
    @api.response(404, "Customer not found")
    @api.response(400, "The posted Customer data was not valid")
    @api.expect(customer_model)
    @api.marshal_with(customer_model)
    def put(self, customer_id):
        """
        Update a Customer

        This endpoint will update a Customer based the body that is posted
        """
        app.logger.info("Request to Update a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id '{customer_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        customer.deserialize(data)
        customer.id = customer_id
        customer.update()
        return customer.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("delete_customer")
    @api.response(204, "Customer deleted")
    def delete(self, customer_id):
        """
        Delete a Customer

        This endpoint will delete a Customer based the id specified in the path
        """
        app.logger.info("Request to Delete a customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if customer:
            customer.delete()
            app.logger.info("Customer with id [%s] was deleted", customer_id)
            return "", status.HTTP_204_NO_CONTENT
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )


######################################################################
#  PATH: /customers
######################################################################
@api.route("/", strict_slashes=False)
class CustomerCollection(Resource):
    """Handles all interactions with collections of Customers"""

    # ------------------------------------------------------------------
    # LIST ALL CUSTOMERS
    # ------------------------------------------------------------------
    @api.doc("list_customers")
    @api.expect(customer_args, validate=True)
    @api.marshal_list_with(customer_model)
    def get(self):
        """Returns all of the Customers"""
        app.logger.info("Request to list customers...")
        args = customer_args.parse_args()
        customers = []

        if args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            customers = Customer.find_by_name(args["name"])
        elif args["email"]:
            app.logger.info("Filtering by email: %s", args["email"])
            customers = Customer.find_by_email(args["email"])
        elif args["address"]:
            app.logger.info("Filtering by address: %s", args["address"])
            customers = Customer.find_by_address(args["address"])
        elif args["active"] is not None:
            active = args["active"].lower() == "true"
            app.logger.info("Filtering by active status: %s", active)
            customers = Customer.find_by_active(active)
        else:
            app.logger.info("Returning all customers")
            customers = Customer.all()

        app.logger.info("[%s] Customers returned", len(customers))
        return [customer.serialize() for customer in customers], status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("create_customer")
    @api.response(400, "Invalid data")
    @api.expect(customer_model, validate=True)
    @api.marshal_with(customer_model, code=201)
    def post(self):
        """Creates a Customer"""
        app.logger.info("Request to create a new customer")
        data = request.json
        customer = Customer()
        customer.deserialize(data)
        customer.create()
        app.logger.info("Customer with ID [%s] created", customer.id)
        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /customers/{id}/activate
######################################################################
@api.route("/customers/<int:customer_id>/activate")
@api.param("customer_id", "The Customer identifier")
class ActivateResource(Resource):
    """Activate actions on a Customer"""

    @api.doc("activate_customers")
    @api.response(404, "Customer not found")
    @api.response(200, "Customer activated")
    def patch(self, customer_id):
        """
        Activate a Customer

        This endpoint will activate a Customer and make it active
        """
        app.logger.info("Request to activate a Customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id [{customer_id}] not found.",
            )
        customer.active = True
        customer.update()
        app.logger.info("Customer with id [%s] has been activated!", customer.id)
        return {
            "message": "Customer activated",
            "active_status": customer.active,
        }, status.HTTP_200_OK


######################################################################
#  PATH: /customers/{id}/deactivate
######################################################################
@api.route("/customers/<int:customer_id>/deactivate")
@api.param("customer_id", "The Customer identifier")
class DeactivateResource(Resource):
    """Deactivate actions on a Customer"""

    @api.doc("deactivate_customers")
    @api.response(404, "Customer not found")
    @api.response(200, "Customer deactivated")
    def patch(self, customer_id):
        """
        Deactivate a Customer

        This endpoint will deactivate a Customer and make it non-active
        """
        app.logger.info("Request to deactivate a Customer with id [%s]", customer_id)
        customer = Customer.find(customer_id)
        if not customer:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Customer with id [{customer_id}] not found.",
            )
        customer.active = False
        customer.update()
        app.logger.info("Customer with id [%s] has been deactivated!", customer.id)
        return {
            "message": "Customer deactivated",
            "active_status": customer.active,
        }, status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
