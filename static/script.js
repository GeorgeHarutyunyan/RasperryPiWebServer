var socket = io();
socket.on('connect', function() {
    console.log('connected');
});
socket.on('message event', function(msg) {
    var ul = document.getElementById("ard-data");
    var li = document.createElement('li');
    li.appendChild(document.createTextNode(msg));
    ul.appendChild(li);
    console.log(msg);
});

window.onload=function(){
    document.getElementById("sendButton").addEventListener("click", function(event){
    event.preventDefault();
    socket.emit('arduino message',document.getElementById("input-message").value);
    document.getElementById("input-message").value = "";
    console.log('button clicked');
});
}
