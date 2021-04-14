// Wait for the DOM to be ready
$(function() {

    // Load symbols table
    $("#symbols").DataTable({
        scrollX: true,
        scrollY: "35rem",
        scrollCollapse: true,
        order: [[0, "asc"]],
        ajax: {
            url: "/symbols_json",
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
            {"data": "Symbol"},
            {"data": "Issuer"},
        ],
    });

});
