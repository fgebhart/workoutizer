// Enable Navbar Dropdown
$(document).ready(function () {
    $(".dropdown-trigger").dropdown({
        coverTrigger: false
    });
});


// enable sidenav
document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('.sidenav');
    var instances = M.Sidenav.init(elems, options);
});

// Initialize collapsible (uncomment the lines below if you use the dropdown variation)
// var collapsibleElem = document.querySelector('.collapsible');
// var collapsibleInstance = M.Collapsible.init(collapsibleElem, options);

// Or with jQuery

$(document).ready(function () {
    $('.sidenav').sidenav();
});

// enable form select
document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, options);
});

// Or with jQuery

$(document).ready(function () {
    $('select').formSelect();
});


// enable button when form is filled
$('#button').attr('disabled', true);
$('input:text').keyup(function () {
    var disable = false;
    $('input:text').each(function () {
        if ($(this).val() == "") {
            disable = true;
        }
    });
    $('#button').prop('disabled', disable);
});