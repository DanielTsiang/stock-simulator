// Wait for the DOM to be ready
$(function() {
    // Change button to spinner when form submits
    $("form").submit(function() {
        // disable submit button
        $("button[type='submit']").prop("disabled", true);

        // add spinner to submit button
        $("button[type='submit']").html(
            `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
        );
    });
});
