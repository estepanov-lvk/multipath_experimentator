"use strict"

let socket = null

function updateServerState() {
    const SERVER_NAME = 0;
    let table = document.getElementById('serverTable'); 
    let tableRows = table.getElementsByTagName('tbody')[0].rows;
    let servers = [];
    let cellRowSpan = 0;
    for (let i = 0; i < tableRows.length; i++) {
        let firstCell = tableRows[i].cells[SERVER_NAME];
        if (cellRowSpan != 0 && cellRowSpan != null) {
            cellRowSpan--;
            continue;
        } else {
            cellRowSpan = firstCell.getAttribute('rowspan')
        }

        let cellText = firstCell.getElementsByTagName('a')[0].text
        servers.push(cellText);
    }
    socket.emit('updateServerState', servers);
}

function updateServerStateTable(server) {
    const SERVER_NAME = 0;
    const SERVER_STATE = 2;
    
    let table = document.getElementById('serverTable'); 
    let tableRows = table.getElementsByTagName('tbody')[0].rows;
    let cellRowSpan = 0;
    for (let i = 0; i < tableRows.length; i++) {
        let firstCell = tableRows[i].getElementsByTagName('td')[SERVER_NAME];
        // first cell in the row can have the rowspan attribute
        if (cellRowSpan != 0 && cellRowSpan != null) {
            cellRowSpan--;
            continue;
        } else {
            cellRowSpan = firstCell.getAttribute('rowspan')
        }
        let node = firstCell.getElementsByTagName('a')[0]
        if (node.text != server.serverName) continue;
        
        let stateCell = tableRows[i].getElementsByTagName('td')[SERVER_STATE];
        if (server.serverState == "Доступен") {
            stateCell.style.color = "green";
        } else {
            stateCell.style.color = "red";
        }
        stateCell.innerHTML = server.serverState
    }
}

// Client Side Javascript to receive server and interface state.
$(document).ready(function(){
    // start up the SocketIO connection to the server - the namespace 'test' is also included here if necessary
    socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    // this is a callback that triggers when the "my response" event is emitted by the server.
    socket.on('test_msg', function(msg) {
        console.log("Received !")
        console.log('<p>Received: ' + msg.data + '</p>');
    });
    socket.on('updatedServerState', updateServerStateTable);

    updateServerState()
    //socket.emit('updateServerState', {dat: "1"});
    //console.log($servers)
});

