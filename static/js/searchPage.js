$(document).ready(function() {
    $('#filterBy a.dropdown-item').on('click', function (e) {
    e.preventDefault()
    var filterParam = $(this).text()
//    console.log(x)
    $('#filter').html(filterParam)
    });


});