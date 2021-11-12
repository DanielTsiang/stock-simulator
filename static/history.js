// Wait for the DOM to be ready
$(function() {

    // Configure date sorting
    $.fn.dataTable.moment("DD-MM-YYYY HH:mm:ss");

    // Load history table
    let historyDataTable = $("#history").DataTable({
        scrollX: true,
        scrollY: "35rem",
        scrollCollapse: true,
        order: [[3, "desc"]],
        ajax: {
            url: "/history_json",
            type: "GET",
            dataType: "json",
            dataSrc: "data",
            contentType:"application/json"
        },
        processing: true,
        language: {
            processing: '<i class="fa fa-spinner fa-spin fa-3x fa-fw"></i><span class="sr-only">Loading...</span> '
        },
        columns: [
            {"data": "symbol"},
            {"data": "shares"},
            {"data": "price"},
            {"data": "transacted"},
        ],
    });

    // Clear history when button clicked
    $("#clear-history").on("click", function(event) {
        $.ajax({
            url: "/history",
            method: "DELETE",
            beforeSend: function() {
                $("#loading-overlay").fadeIn(300);
            },
            success: function(response){
                // Hide and remove Modal
                $("#historyModal").modal("hide");
                $("body").removeClass("modal-open");
                $(".modal-backdrop").remove();

                // Reload DataTable
                historyDataTable.ajax.reload();
            },
            complete: function() {
                $("#loading-overlay").fadeOut(300);
            },
            error: function(xhr, status, error) {
                alert(`${status}: ${error}`);
            }
        });
    });

    // Disable clear history button until checkbox is checked
    $("#checkbox").change(function() {
        $("#clear-history").prop("disabled", !this.checked); //true: disabled, false: enabled
    }).change(); //trigger event

    // Reset all modals when hidden
	$(".modal").on("hidden.bs.modal", function(){
	    // Define alias for checkbox
	    let chkbox = $("#checkbox");

	    // Reset checkbox to unchecked
        chkbox.prop("checked", false);
        // Reset clear history button to disabled
        $("#clear-history").prop("disabled", !chkbox.checked);
    });

});
