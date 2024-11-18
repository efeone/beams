$(document).ready(function () {
    // Initialize the filter flag to false when the page loads
    var filterFlag = false;

    // Event listener for changes in the filter fields
    $('#designation, #location, #type').change(function () {
        // Get the selected values from the filter fields
        var designation = $('#designation').val();
        var location = $('#location').val();
        var type = $('#type').val();

        // Construct the URL with the selected filter values
        var url = '/job_portal/?designation=' + designation + '&location=' + location + '&employment_type=' + type;

        // Redirect to the constructed URL
        window.location.href = url;

        // Update the filter flag to true when the filter is applied
        filterFlag = true;
    });
});