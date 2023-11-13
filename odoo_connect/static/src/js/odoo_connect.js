// hide footer from documentation page
odoo.define('odoo_connect.hide_documentation_footer', function (require) {
    'use strict';

    $(document).ready(function () {
        // Get the current page's URL
        var currentPageUrl = window.location.pathname;

        // Extract the unique identifier from the URL
        var uniqueIdentifier = currentPageUrl.match(/\/documentation\/(\d+)/);

        // Check if a unique identifier was found and hide the footer if it matches a specific value (e.g., 2)
        if (uniqueIdentifier) {
            // Hide the footer element (replace 'footer-selector' with the actual selector of your footer)
            $('footer').hide();
        }
    });
});