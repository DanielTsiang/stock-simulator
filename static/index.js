// Wait for the DOM to be ready
$(function() {
    // Initialize Select2 for quote and buy modal form
    $(".select2-form").select2({
        placeholder: "Select a symbol",
        width: "50%",
        theme: 'bootstrap4',
        minimumInputLength : 1,
        language: {
            inputTooShort: function (args) {
                return "Start typing to search";
            },
        },
        ajax: {
        	url: "/select_json",
        	dataType: "json",
        	type: "GET",
        	delay: 250,
            data: function(params) {
                return {
                    q: params.term
                };
            },
            processResults: function(data) {
                return {
                    results: $.map(data.symbols, function(item) {
                        return {
                            id: item.Symbol,
                            text: item.Symbol,
                        };
                    })
                };
            },
        },
    });

    // Initialize Select2 for sell modal form
    $("#symbol-sell").select2({
        placeholder: "Select a symbol",
        width: "50%",
        theme: 'bootstrap4',
        ajax: {
        	url: "/sell_json",
        	dataType: "json",
        	type: "GET",
        	delay: 250,
            data: function(params) {
                return {
                    q: params.term
                };
            },
            processResults: function(data) {
                return {
                    results: $.map(data.symbols, function(item) {
                        return {
                            id: item.symbol,
                            text: item.symbol,
                        };
                    })
                };
            },
        },
    });

    // Focus on select2 search field when opened
    $(document).on("select2:open", () => {
        document.querySelector(".select2-search__field").focus();
    });

    // Select2 search field placeholder
    $(document).on("select2:open", () => {
        $('.select2-search__field').attr('placeholder', 'Search symbols');
    });

    // Remove text-center class on select2 and add text-left class instead
    $(".select2-selection--single").removeClass("text-center").addClass("text-left");

    // Fix select2 inside Bootstrap modal
    $.fn.modal.Constructor.prototype._enforceFocus = function() {};

    // Load shares table via AJAX
	let sharesTable = $("#shares").DataTable({
		scrollX: true,
		scrollY: "35rem",
		scrollCollapse: true,
		order: [[0, "asc"]],
		ajax: {
			url: "/index_json",
			type: "GET",
			dataType: "json",
			dataSrc: "shares_data",
			contentType:"application/json"
		},
		processing: true,
        language: {
            processing: '<i class="fa fa-spinner fa-spin fa-3x fa-fw"></i><span class="sr-only">Loading...</span> '
        },
		columns: [
			{"data": "symbol"},
			{"data": "name"},
			{"data": "shares_count"},
			{
			    "render": $.fn.dataTable.render.number(",", ".", 2, "$"),
			    "data": "price"
		    },
			{
			    "render": $.fn.dataTable.render.number(",", ".", 2, "$"),
			    "data": "total"
			},
		],
	});

    // Ajax event, fired when an Ajax request is completed, i.e. when DataTables has completed the loading of data
    sharesTable.on( 'xhr.dt', function( event, settings, json, xhr) {
        let priceFormat = $.fn.dataTable.render.number("\,", ".", 2, "$").display;

        let shares_sum = 0;
        json["shares_data"].forEach((element, index, array) => {
            shares_sum += element.total;
        });

        let total_sum = shares_sum + json["cash_data"];

        // Update shares table footers
        $("tfoot>tr>td#cash").html(priceFormat(json["cash_data"]));
        $("tfoot>tr>td#total").html(priceFormat(total_sum));
    });

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
        errorPlacement: function(error, element, errorClass) {
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

    // Initialize form validation for quote form
    $("form[name='quote']").validate({
        // Specify validation rules
        rules: {
            symbol_quote: {
                required: true,
                symbol_check: true,
                remote: {
                    url: "/symbol_check",
                    type: "GET"
                }
            },
        },
        // Specify validation error messages
        messages: {
            symbol_quote: {
                required: "Please enter a symbol",
                symbol_check: "Please only enter valid symbol characters",
                remote: "Invalid symbol!",
            },
        },
        // Submit form when valid
        submitHandler: function(form) {
            $.ajax({
                url: "/quote",
                method: "GET",
                data: {
                    symbol_quote: $(form).find("select[name='symbol_quote']").val(),
                },
                dataType: "json",
                beforeSend: function() {
                    $("#loading-overlay").fadeIn(300);
                },
                success: function(response) {
                    // Reset form fields
                    $("#quote-form")[0].reset();

                    // Remove validation classes and errorElements
                    $("input, span, div, select").removeClass("is-invalid is-valid");
                    $("#symbol-quote-error").remove();

                    // Create our number formatter.
                    let formatter = new Intl.NumberFormat('en-US', {
                        style: 'currency',
                        currency: 'USD',
                    });

                    // Display stock information
                    let QUOTED = response.QUOTED;
                    let symbol = response.symbol;
                    $("#quoted").html(`A share of ${QUOTED[symbol]["longName"]} (${symbol}) costs ${formatter.format(QUOTED[symbol]["currentPrice"])}.`);
                },
                complete: function() {
                    $("#loading-overlay").fadeOut(300);
                },
                error: function(xhr, status, error) {
                    alert(`${status}: ${error}`);
                }
            });
        }
    });

    // Initialize form validation for buy form
    $("form[name='buy']").validate({
        // Specify validation rules
        rules: {
            symbol_buy: {
                required: true,
                symbol_check: true,
                remote: {
                    url: "/symbol_check",
                    type: "GET"
                }
            },
            shares_buy: {
                required: true,
                remote: {
                    url: "/buy_check",
                    type: "GET",
                    beforeSend: function() {
                        $("#shares-buy").addClass("loading");
                    },
                    complete: function() {
                        $("#shares-buy").removeClass("loading");
                    },
                    data: {
                        // Send additional data along with the default data
                        symbol_buy: function() {
                            return $("#symbol-buy").val();
                        },
                        shares_buy: function() {
                            return buy.getNumber();
                        },
                    },
                }
            },
        },
        // Specify validation error messages
        messages: {
            symbol_buy: {
                required: "Please enter a symbol",
                symbol_check: "Please only enter valid symbol characters",
                remote: "Invalid symbol!",
            },
            shares_buy: {
                required: "Please enter a share quantity",
                remote: "You don't have enough cash!",
            },
        },
        // Submit form when valid
        submitHandler: function(form) {
            $.ajax({
                url: "/buy",
                method: "PUT",
                data: {
                    symbol_buy: $(form).find("select[name='symbol_buy']").val(),
                    shares_buy: buy.getNumber(), // Return the unformatted number from autoNumeric method
                },
                dataType: "json",
                beforeSend: function() {
                    $("#loading-overlay").fadeIn(300);
                },
                success: function() {
                    // Reset form
                    $("form[name='buy']")[0].reset();

                    // Hide and remove Modal
                    $("#buyModal").modal("hide");
                    $("body").removeClass("modal-open");
                    $(".modal-backdrop").remove();

                    // Reload DataTable
                    sharesTable.ajax.reload();

                    // Show bought alert
                    $("#buy-alert").fadeIn();

                 },
                complete: function() {
                    $("#loading-overlay").fadeOut(300);
                },
                error: function(xhr, status, error) {
                    alert(`${status}: ${error}`);
                }
            });
        }
    });

    // Initialize form validation for sell form
    $("form[name='sell']").validate({
        // Specify validation rules
        rules: {
            symbol_sell: {
                required: true,
                symbol_check: true,
                remote: {
                    url: "/symbol_check",
                    type: "GET"
                }
            },
            shares_sell: {
                required: true,
                remote: {
                    url: "/sell_check",
                    type: "GET",
                    beforeSend: function() {
                        $("#shares-sell").addClass("loading");
                    },
                    complete: function() {
                        $("#shares-sell").removeClass("loading");
                    },
                    data: {
                        // Send additional data along with the default data
                        symbol_sell: function() {
                            return $("#symbol-sell").val();
                        },
                        shares_sell: function() {
                            return sell.getNumber();
                        },
                    },
                }
            },
        },
        // Specify validation error messages
        messages: {
            symbol_sell: {
                required: "Please enter a symbol",
                symbol_check: "Please only enter valid symbol characters",
                remote: "Invalid symbol!",
            },
            shares_sell: {
                required: "Please enter a share quantity",
                remote: "You don't have enough shares to sell!",
            },
        },
        // Submit form when valid
        submitHandler: function(form) {
            $.ajax({
                url: "/sell",
                method: "PUT",
                data: {
                    symbol_sell: $(form).find("select[name='symbol_sell']").val(),
                    shares_sell: sell.getNumber(), // Return the unformatted number from autoNumeric method
                },
                dataType: "json",
                beforeSend: function() {
                    $("#loading-overlay").fadeIn(300);
                },
                success: function() {
                    // Reset form
                    $("form[name='sell']")[0].reset();

                    // Hide and remove Modal
                    $("#sellModal").modal("hide");
                    $("body").removeClass("modal-open");
                    $(".modal-backdrop").remove();

                    // Reload DataTable
                    sharesTable.ajax.reload();

                    // Show bought alert
                    $("#sell-alert").fadeIn();

                 },
                complete: function() {
                    $("#loading-overlay").fadeOut(300);
                },
                error: function(xhr, status, error) {
                    alert(`${status}: ${error}`);
                }
            });
        }
    });

    // Initialize form validation for cash form
    $("form[name='cash']").validate({
        // Specify validation rules
        rules: {
            cash: {
                required: true,
            },
        },
        // Specify validation error messages
        messages: {
            cash: {
                required: "Please enter a cash amount",
            },
        },
        // Submit form when valid
        submitHandler: function(form) {
            $.ajax({
                url: "/cash",
                method: "PUT",
                data: {
                    cash: cash.getNumber(), // Return the unformatted number from autoNumeric method
                },
                dataType: "json",
                beforeSend: function() {
                    $("#loading-overlay").fadeIn(300);
                },
                success: function() {
                    // Reset form
                    $("form[name='cash']")[0].reset();

                    // Hide and remove Modal
                    $("#cashModal").modal("hide");
                    $("body").removeClass("modal-open");
                    $(".modal-backdrop").remove();

                    // Reload DataTable
                    sharesTable.ajax.reload();

                    // Show bought alert
                    $("#cash-alert").fadeIn();

                 },
                complete: function() {
                    $("#loading-overlay").fadeOut(300);
                },
                error: function(xhr, status, error) {
                    alert(`${status}: ${error}`);
                }
            });
        }
    });

    // Valid symbol characters check
    $.validator.addMethod("symbol_check", function(value) {
        return /^[a-zA-Z \.^#=+-]+$/.test(value); // check only valid symbol characters entered
    });

    // Fade out dismissible alert message, allows alert message to fade back in later
	$(function(){
		$("[data-hide]").on("click", function() {
			$(this).closest("." + $(this).attr("data-hide")).fadeOut();
		});
	});

	// Reset all modals when hidden
	$(".modal").on("hidden.bs.modal", function(){
	    // Reset all form fields and validation on page
        $("form").each( function() {
	        this.reset();
	        $(this).validate().resetForm();
        });

	    // Remove errorElements and validation classes
	    $("span[class=has-error]").remove();
        $("input, span, div, select").removeClass("is-invalid is-valid");

        // Remove stock quote text
        $("#quoted").html("");

        // Reset text for select option to placeholder
        $(".select2-placeholder").val(null).trigger('change');
    });

    // Every time a modal is shown, if it has an autofocus element, focus on it.
    $(".modal").on("shown.bs.modal", function() {
        $(this).find("[autofocus]").focus();
    });

    // Initialise AutoNumeric on number input forms
    let cash = new AutoNumeric("#cash-input", {minimumValue: 0});
    let buy = new AutoNumeric("#shares-buy", {decimalPlaces: 0, minimumValue: 0});
    let sell = new AutoNumeric("#shares-sell", {decimalPlaces: 0, minimumValue: 0});

});
