$(document).ready(function() {

    namespace='/plan_4g';

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

    socket.on('connect', function() {
        $('#log').append('Client: Client connected...'+'<br>');
    });

    socket.on('my_response', function(msg) {
        $('#log').append($('<div/>').text(msg.message).html()+'<br>');
    });

    socket.on('progress', function(msg) {
        $('#log').append($('<div/>').text(msg.message).html()+'<br>');
    });

    socket.on('disconnect', function() {
        $('#log').append('Client: Client disconnected...'+'<br>');
//        $("#downloadButton").removeAttr("disabled");
//        console.log('Disconnected!!!');

    });

    socket.on('plan finished', function(msg) {
        $('#log').append('Client: Plan finished...'+'<br>');
        $("#downloadButton").removeAttr("disabled");
        alert("Plan finished!!!");
        console.log('Plan finished!!!');
    });

    socket.on('plan error', function(msg) {
         $('#log').append('Client: Client disconnected...'+'<br>');
    });

    $('form#plan').submit(function(event) {
        $('#log').append('Client: Plan submitted...'+'<br>');
        socket.emit('plan',{rCol:$('#rCol').val(),rMod3:$('#rMod3').val(),rMin:$('#rMin').val()});
        return false;
    });

});