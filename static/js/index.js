
// Wait for the DOM to be ready
$(document).ready(function () {
    // Add a submit event listener to the form
    $('#playlistForm').submit(function (event) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // Serialize the form data
        const formData = $(this).serialize();

        // Send the form data via AJAX to the 'processurl' endpoint
        $.post('/processurl', formData)
            .done(function (response) {
                // Handle successful response
                console.log('Form data sent successfully');
            })
            .fail(function (xhr, status, error) {
                // Handle errors
                console.error('Error sending form data:', error);
            });
    });
});
