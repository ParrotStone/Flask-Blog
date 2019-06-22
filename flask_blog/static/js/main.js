// Initialize the side-navigation plugin
document.addEventListener('DOMContentLoaded', function () {
    const elems = document.querySelectorAll('.sidenav');
    const instances = M.Sidenav.init(elems, {});
});

$(document).ready(function () {
    // Initialize the character counter plugin for input fields - It needs jQuery to initialize the plugin
    $('.media-container .input-field input#username').characterCounter();
    // Remove the alerts after 4 seconds
    setTimeout(() => {
        $('.alert').fadeOut();
    }, 4000);
});
