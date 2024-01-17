document.addEventListener('DOMContentLoaded', function() {
    var details = document.querySelectorAll('details');

    details.forEach(function(detail) {
        detail.addEventListener('toggle', function() {
            // Do nothing when an accordion is opened or closed
        });
    });
});