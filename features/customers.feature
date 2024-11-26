Feature: The Customer service back-end
    As an E-commerce Website
    I need a RESTful Customer management service
    So that I can keep track of all my Customer information

Background:
    Given the following Customers
        | name       | email                  | active    | address   | id     | password  |
        | fido       | fido123@gmail.com      | True      | 12-abc    | 123456 | pass      |
        | kitty      | kitty123@gmail.com     | True      | 34-efd    | 456789 | word      |
        | leo        | leo123@gmail.com       | False     | 56-jkl    | 765432 | something |
        | sammy      | sammy123@gmail.com     | True      | 78-uio    | 543634 | nothing   |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Customer REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Customer
    When I visit the "Home Page"
    And I set the "Name" to "fido"
    And I set the "Email" to "fido123@gmail.com"
    And I select "True" in the "Active" dropdown
    And I set the "Address" to "My-place"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Active" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "fido" in the "Name" field
    And I should see "fido123@gmail.com" in the "Email" field
    And I should see "True" in the "Active" dropdown
    And I should see "My-place" in the "Address" field

Scenario: Read a Customer
    When I visit the "Home Page"
    And I set the "Id" to "123456"
    And I press the "Retrieve" button
    Then I should see "fido" in the "Name" field
    And I should see "fido123@gmail.com" in the "Email" field
    And I should see "True" in the "Active" dropdown
    And I should see "12-abc" in the "Address" field

Scenario: Update a Customer
    When I visit the "Home Page"
    And I set the "Name" to "fido"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the "Name" field
    And I should see "True" in the "Active" field
    When I change "Name" to "Loki"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Loki" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Loki" in the results
    And I should not see "fido" in the results

Scenario: Delete a Customer
    When I visit the "Home Page"
    And I set the "Id" to "123456"
    And I press the "Delete" button
    Then I should see the message "Success"
    And I should not see "fido" in the results

Scenario: List all pets
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should see "kitty" in the results
    And I should see "leo" in the results

Scenario: Search for Name "sammy"
    When I visit the "Home Page"
    And I set the "Name" to "sammy"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "sammy" in the results
    And I should not see "fido" in the results
    And I should not see "kitty" in the results

Scenario: Search for Active
    When I visit the "Home Page"
    And I select "True" in the "Active" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "fido" in the results
    And I should see "kitty" in the results
    And I should see "sammy" in the results
    And I should not see "leo" in the results

Scenario: Deactivate a Customer
    When I visit the "Home Page"
    And I set the "Id" to "123456"
    And I press the "Retrieve" button
    Then I should see "fido" in the "Name" field
    And I should see "True" in the "Active" dropdown
    When I select "False" in the "Active" dropdown
    And I press the "Deactivate" button
    Then I should see the message "Customer has been Deactivated!"
    And I should see "False" in the "Active" dropdown

Scenario: Activate a Customer
    When I visit the "Home Page"
    And I set the "Id" to "765432"
    And I press the "Retrieve" button
    Then I should see "leo" in the "Name" field
    And I should see "False" in the "Active" dropdown
    When I select "True" in the "Active" dropdown
    And I press the "Activate" button
    Then I should see the message "Customer has been Activated!"
    And I should see "True" in the "Active" dropdown