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
            error.addClass("invalid-feedback");
            error = error.css("display", "block");

			if (element.parent(".input-group").length) {
				error.insertAfter(element.parent());
			} else if (element.hasClass("select2-hidden-accessible")) {
				error.insertAfter(element.siblings(".select2-container"));
			} else {
		      error.insertAfter(element);
			}
        },
    });

    // Initialize form validation on the change password form.
    $("form[name='password']").validate({
        // Disable validation on keyup event
        onkeyup: false,
        // Specify validation rules
        rules: {
            old_password: {
                required: true,
                remote: {
                    url: "/passwordCheck",
                    type: "POST",
                    beforeSend: function() {
                        $("#old-password").addClass("loading");
                    },
                    complete: function() {
                        $("#old-password").removeClass("loading");
                    }
                }
            },
            new_password: {
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
                equalTo: "#new-password",
                beforeSend: function() {
                    $("#info-icon2").css("display", "none");
                },
            },
        },
        // Specify validation error messages
        messages: {
            old_password: {
                required: "Please enter your old password",
                remote: "Incorrect old password!"
            },
            new_password: {
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
            $.ajax({
                url: "/password",
            	method: "PATCH",
                data: {
                    old_password: $(form).find("input[name='old_password']").val(),
                    new_password: $(form).find("input[name='new_password']").val(),
                    confirmation: $(form).find("input[name='confirmation']").val(),
	    });

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
