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
from flask import abort  # , request
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse, inputs
from service.models import Customer
from service.common import status

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
        "id": fields.Integer(
            description="The unique id assigned internally by service",
            readOnly=True,
        ),
    },
)


######################################################################
# Setup the request parser for customers
######################################################################
args_config = [
    ("name", str, "args", False, "Filter customers by name"),
    ("id", int, "args", False, "Filter customers by customer ID"),
    ("email", str, "args", False, "Filter customers by email"),
    ("address", str, "args", False, "Filter customers by address"),
    (
        "active",
        inputs.boolean,
        "args",
        False,
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
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": 200, "message": "Healthy"}, status.HTTP_200_OK


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
@api.route("/customers/<customer_id>")
@api.param("customer_id", "The Customer identifier")
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
    @api.expect(create_model)
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
    @api.response(400, "The posted Customer data was not valid")
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


######################################################################
#  PATH: /customers
######################################################################
@api.route("/customers", strict_slashes=False)
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
            app.logger.info("Filtering by active status: %s", args["active"])
            customers = Customer.find_by_active(args["active"])
        else:
            app.logger.info("Returning all customers")
            customers = Customer.all()

        # This app logger is bugged, not worth fixing.. pls ignore
        # app.logger.info("[%s] Customers returned", len(customers))
        return [customer.serialize() for customer in customers], status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW CUSTOMER
    # ------------------------------------------------------------------
    @api.doc("create_customer")
    @api.response(400, "Invalid data")
    @api.expect(create_model)
    @api.marshal_with(customer_model, code=201)
    def post(self):
        """Creates a Customer"""
        app.logger.info("Request to create a new customer")
        # data = request.json
        customer = Customer()
        customer.deserialize(api.payload)
        customer.create()
        app.logger.info("Customer with ID [%s] created", customer.id)
        location_url = api.url_for(
            CustomerResource, customer_id=customer.id, _external=True
        )
        return customer.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /customers/{id}/activate
######################################################################
@api.route("/customers/<customer_id>/activate")
@api.param("customer_id", "The Customer identifier")
class ActivateResource(Resource):
    """Activate actions on a Customer"""

    @api.doc("activate_customers")
    @api.response(404, "Customer not found")
    def put(self, customer_id):
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
        return customer.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /customers/{id}/deactivate
######################################################################
@api.route("/customers/<customer_id>/deactivate")
@api.param("customer_id", "The Customer identifier")
class DeactivateResource(Resource):
    """Deactivate actions on a Customer"""

    @api.doc("deactivate_customers")
    @api.response(404, "Customer not found")
    def put(self, customer_id):
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
        return customer.serialize(), status.HTTP_200_OK
