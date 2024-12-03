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
TestCustomer API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import quote_plus
from wsgi import app
from service.common import status
from service.models import db, Customer, DataValidationError
from .factories import CustomerFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomerService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    ############################################################
    # Utility function to bulk create customers
    ############################################################
    def _create_customers(self, count: int = 1) -> list:
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            response = self.client.post(BASE_URL, json=test_customer.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test customer",
            )
            new_customer = response.get_json()
            test_customer.id = new_customer["id"]
            customers.append(test_customer)
        return customers

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    # ----------------------------------------------------------
    # TEST INVALID METHODS
    # ----------------------------------------------------------
    def test_delete_invalid_methods(self):
        """It should throw HTTP 405, METHOD_NOT_ALLOWED"""
        response = self.client.delete(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        self._create_customers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_customer(self):
        """It should Get a single Customer"""
        # get the id of a customer

        test_customer = self._create_customers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["id"], test_customer.id)
        self.assertEqual(data["name"], test_customer.name)
        self.assertEqual(data["password"], test_customer.password)
        self.assertEqual(data["email"], test_customer.email)
        self.assertEqual(data["address"], test_customer.address)
        self.assertEqual(data["active"], test_customer.active)

    def test_get_customer_not_found(self):
        """It should not Get a Customer thats not found"""
        non_existent_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"{BASE_URL}/{non_existent_uuid}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------

    def test_create_customer(self):
        """It should Create a new Customer"""
        test_customer = CustomerFactory()
        logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["id"], test_customer.id)
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["password"], test_customer.password)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["active"], test_customer.active)

        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_customer = response.get_json()
        self.assertEqual(new_customer["id"], test_customer.id)
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["password"], test_customer.password)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["active"], test_customer.active)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_customer(self):
        """It should Update an existing Customer"""
        # create a customer to update
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = response.get_json()
        logging.debug(new_customer)
        new_customer["address"] = "unknown"
        response = self.client.put(
            f"{BASE_URL}/{new_customer['id']}", json=new_customer
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_customer = response.get_json()
        self.assertEqual(updated_customer["address"], "unknown")

    def test_update_customer_not_found(self):
        """It should not Update a Customer thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_customer(self):
        """It should Delete a Customer"""
        test_customer = self._create_customers(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_customer(self):
        """It should Delete a Customer even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------
    def test_query_by_name(self):
        """It should Query Customers by name"""
        customers = self._create_customers(5)
        test_name = customers[0].name
        name_count = len(
            [customer for customer in customers if customer.name == test_name]
        )
        response = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["name"], test_name)

    def test_query_by_email(self):
        """It should Query Customers by email"""
        customers = self._create_customers(5)
        test_email = customers[0].email
        name_count = len(
            [customer for customer in customers if customer.email == test_email]
        )
        response = self.client.get(
            BASE_URL, query_string=f"email={quote_plus(test_email)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["email"], test_email)

    def test_query_customer_list_by_address(self):
        """It should Query Customers by Category"""
        customers = self._create_customers(10)
        test_address = customers[0].address
        address_customers = [
            customer for customer in customers if customer.address == test_address
        ]
        response = self.client.get(
            BASE_URL, query_string=f"address={quote_plus(test_address)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(address_customers))
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["address"], test_address)

    def test_query_by_activeness(self):
        """It should Query Customers by activeness"""
        customers = self._create_customers(10)
        active_customers = [
            customer for customer in customers if customer.active is True
        ]
        inactive_customers = [
            customer for customer in customers if customer.active is False
        ]
        active_count = len(active_customers)
        inactive_count = len(inactive_customers)
        logging.debug("Available Customers [%d] %s", active_count, active_customers)
        logging.debug("Inactive Customers [%d] %s", inactive_count, inactive_customers)

        # test for active
        response = self.client.get(BASE_URL, query_string="active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), active_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["active"], True)

        # test for inactive
        response = self.client.get(BASE_URL, query_string="active=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), inactive_count)
        # check the data just to be sure
        for customer in data:
            self.assertEqual(customer["active"], False)

    # ----------------------------------------------------------
    # TEST ACTIONS
    # ----------------------------------------------------------
    def test_deactivate_customer(self):
        """It should Deactivate a Customer account"""
        customer = CustomerFactory()
        logging.debug("Test Customer: %s", customer.serialize())
        response = self.client.post(BASE_URL, json=customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.put(f"{BASE_URL}/{customer.id}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f"{BASE_URL}/{customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["active"], False)

        bad_customer = CustomerFactory()
        response = self.client.put(f"{BASE_URL}/{bad_customer.id}/deactivate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


######################################################################
#  T E S T   S A D   P A T H S
######################################################################
class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_method_not_allowed(self):
        """It should not allow update without a customer id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_customer_no_data(self):
        """It should not Create a Customer with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_content_type(self):
        """It should not Create a Customer with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_wrong_content_type(self):
        """It should not Create a Customer with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_find_customer_not_found(self):
        """It should return a 404 error if customer is not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  T E S T   M O C K S
    ######################################################################

    @patch("service.routes.Customer.find_by_name")
    def test_bad_request_name(self, bad_request_mock):
        """It should return a Bad Request error from Find By Name"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="name=fido")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("service.routes.Customer.find_by_email")
    def test_bad_request_email(self, bad_request_mock):
        """It should return a Bad Request error from Find By Email"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="email=fido")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("service.routes.Customer.find_by_address")
    def test_bad_request_address(self, bad_request_mock):
        """It should return a Bad Request error from Find By Address"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="address=fido")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("service.routes.Customer.find_by_active")
    def test_bad_request_active(self, bad_request_mock):
        """It should return a Bad Request error from Find By Active"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="active=fido")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
