// Wait for the DOM to be ready
$(function() {
    $.validator.setDefaults({
        errorElement: "span",
        errorClass: "is-invalid",
        validClass: "is-valid",
        highlight: function(element, errorClass, validClass) {
            $(element).addClass(errorClass).removeClass(validClass);
        },
        unhighlight: function(element, errorClass, validClass) {
            $(element).removeClass(errorClass).addClass(validClass);
        },
        errorPlacement: function(error, element) {
            // Add the "invalid-feedback" class to the error element and display as block
            // error.addClass("invalid-feedback");
            error = error.css("display", "block");

			if (element.parent(".input-group").length) {
				error.insertAfter(element.parent());
			} else if (element.hasClass("select2-hidden-accessible")) {
				error.insertAfter(element.siblings(".select2-container"));
			} else {
		      error.insertAfter(element);
			}
        },
        success: function(error) {
            error.addClass("is-valid").text("Ok!");
        },
    });

    // Initialize form validation on the registration form.
    // It has the name attribute "registration"
    $("form[name='registration']").validate({
        // Disable validation on keyup event
        onkeyup: false,
        // Specify validation rules
        rules: {
            // The key name on the left side is the name attribute of an input field.
            // Validation rules are defined on the right side.
            username: {
                required: true,
                remote: {
                    url: "/username_check",
                    type: "GET",
                    beforeSend: function() {
                        $("#username").addClass("loading");
                    },
                    complete: function() {
                        $("#username").removeClass("loading");
                    }
                }
            },
            password: {
                required: true,
                minlength: 5,
                pwcheck: true,
                beforeSend: function() {
                    $("#info-icon1").css("display", "none");
                },
            },
            confirmation: {
                required: true,
                minlength: 5,
                equalTo: "#password",
                beforeSend: function() {
                    $("#info-icon2").css("display", "none");
                },
            },
        },
        // Specify validation error messages
        messages: {
            username: {
                required: "Please enter your username",
                remote: "Username is already in use!"
            },
            password: {
                required: "Please provide a password",
                minlength: "Your password must be at least 5 characters long",
                pwcheck: "Your password must contain an uppercase letter and a digit"
            },
            confirmation: {
                required: "Please provide a password confirmation",
                minlength: "Your password must be at least 5 characters long",
                equalTo: "Your passwords do not match"
            }
        },
        // Make sure the form is submitted to the destination defined
        // in the "action" attribute of the form when valid
        submitHandler: function(form) {
            form.submit();

            // disable submit button
            $("button[type='submit']").prop("disabled", true);

            // add spinner to submit button
            $("button[type='submit']").html(
                `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
            );
        }
    });

    // Valid password check
    $.validator.addMethod("pwcheck", function(value) {
        return /[A-Z]/.test(value) // has an uppercase letter
            && /\d/.test(value); // has a digit
    });

    // Initialise all tooltips on page
    $('[data-toggle="tooltip"]').tooltip();

});