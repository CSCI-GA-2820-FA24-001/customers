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
Customer Steps

Steps file for Customers.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests, os
from compare3 import expect
from behave import given, when, then  # pylint: disable=no-name-in-module

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60
ID_PREFIX = "customer_"


@given("the following Customers")
def step_impl(context):
    """Delete all Customers and load new ones"""

    # Get a list all of the pets
    rest_endpoint = f"{context.base_url}/customers"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for customer in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{customer['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new pets
    for row in context.table:
        payload = {
            "name": row["name"],
            "password": row["password"],
            "active": row["active"] in ["True", "true", "1"],
            "id": row["id"],
            "email": row["email"],
            "address": row["address"],
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)


@when('I visit the "Home Page"')
def step_impl(context):
    context.resp = requests.get(context.base_url + "/")
    assert context.resp.status_code == 200


@then('I should see "{message}" in the title')
def step_impl(context, message):
    assert message in str(context.resp.text)


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    assert True  # TODO: erase this line


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    assert True  # TODO: erase this line


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    assert True  # TODO: erase this lined


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    assert True  # TODO: erase this lined


@when('I press the "{button}" button')
def step_impl(context, button):
    assert True  # TODO: erase this lined


@then('I should see "{name}" in the results')
def step_impl(context, name):
    assert True  # TODO: erase this lined


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    assert True  # TODO: erase this lined


@then('I should see the message "{message}"')
def step_impl(context, message):
    assert True  # TODO: erase this lined


@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    assert True  # TODO: erase this lined


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    assert True  # TODO: erase this lined


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    assert True  # TODO: erase this lined


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    assert True  # TODO: erase this lined
