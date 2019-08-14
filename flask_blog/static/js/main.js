// Initialize the side-navigation plugin
document.addEventListener('DOMContentLoaded', function () {
    const elems = document.querySelectorAll('.sidenav');
    const instances = M.Sidenav.init(elems, {});
});

$(document).ready(function () {
    // Initialize the character counter plugin for input fields - It needs jQuery to initialize the plugin
    $('.media-container .input-field input#username').characterCounter();
    $('.media-container .input-field textarea#brief_info').characterCounter();
    $('.media-container .input-field input#title').characterCounter();
    // Remove the alerts after 4 seconds
    setTimeout(() => {
        $('.alert').slideUp(300);
    }, 4000);

    // Activating the Dropdown plugin in Materialize JS
    $('.dropdown-trigger').dropdown({ hover: false });

    // Activating the modal plugin in Materialize JS
    $('.modal').modal();
});
