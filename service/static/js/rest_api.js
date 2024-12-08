const BASE_URL = "/api/customers"

$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.id);
        $("#customer_name").val(res.name);
        $("#customer_email").val(res.email);
        if (res.active == true) {
            $("#customer_active").val("true");
        } else {
            $("#customer_active").val("false");
        }
        $("#customer_address").val(res.address);
        $("#customer_password").val(res.password);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_name").val("");
        $("#customer_email").val("");
        $("#customer_active").val("");
        $("#customer_address").val("");
        $("#customer_password").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Pet
    // ****************************************

    $("#create-btn").click(function () {

        let id = $("#customer_id").val();
        let name = $("#customer_name").val();
        let email = $("#customer_email").val();
        let password = $("#customer_password").val();
        let address = $("#customer_address").val();
        let active = $("#customer_active").val() == "true";

        let data = {
            "id": id,
            "name": name,
            "email": email,
            "password": password,
            "address": address,
            "active": active
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: BASE_URL,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let name = $("#customer_name").val();
        let email = $("#customer_email").val();
        let available = $("#customer_active").val() == "true";
        let address = $("#customer_address").val();
        let password = $("#customer_password").val();

        let data = {
            "id": customer_id,
            "name": name,
            "email": email,
            "active": available,
            "address": address,
            "password": password
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `${BASE_URL}/${customer_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Pet
    // ****************************************

    $("#retrieve-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}/${customer_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${BASE_URL}/${customer_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Customer has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#customer_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Pet
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#customer_name").val();
        let email = $("#customer_email").val();
        let address = $("#customer_address").val();
        let available = $("#customer_active").val() == "true";

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (email) {
            if (queryString.length > 0) {
                queryString += '&email=' + email
            } else {
                queryString += 'email=' + email
            }
        }
        if (address) {
            if (queryString.length > 0) {
                queryString += '&address=' + address
            } else {
                queryString += 'address=' + address
            }
        }
        if (available) {
            if (queryString.length > 0) {
                queryString += '&active=' + available
            } else {
                queryString += 'active=' + available
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${BASE_URL}?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Email</th>'
            table += '<th class="col-md-2">Password</th>'
            table += '<th class="col-md-2">Address</th>'
            table += '<th class="col-md-2">Active</th>'
            table += '</tr></thead><tbody>'
            let firstPet = "";
            for(let i = 0; i < res.length; i++) {
                let pet = res[i];
                table +=  `<tr id="row_${i}"><td>${pet.id}</td><td>${pet.name}</td><td>${pet.email}</td><td></td><td>${pet.address}</td><td>${pet.active}</td></tr>`;
                if (i == 0) {
                    firstPet = pet;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPet != "") {
                update_form_data(firstPet)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Activate a Pet
    // ****************************************

    $("#activate-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `${BASE_URL}/${customer_id}/activate`,
                contentType: "application/json",
                data: ''
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Deactivate a Pet
    // ****************************************

    $("#deactivate-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `${BASE_URL}/${customer_id}/deactivate`,
                contentType: "application/json",
                data: ''
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });


})