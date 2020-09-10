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

function updateVMState() {
    const VM_NAME = 0;
    let table = document.getElementById('vmTable'); 
    let tableRows = table.getElementsByTagName('tbody')[0].rows;
    let vms = [];
    for (let i = 0; i < tableRows.length; i++) {
        let firstCell = tableRows[i].cells[VM_NAME];
        let cellText = firstCell.getElementsByTagName('a')[0].text
        vms.push(cellText);
    }
    socket.emit('updateVMState', vms);
}

function updateInterfaceTable(msg) {
    const SERVER_NAME = 0;
    const INTERFACE_NAME = 4;
    const INTERFACE_NAME_SPAN = 0;
    const INTERFACE_STATUS = 5;
    const INTERFACE_STATUS_SPAN = 1;
    
    console.log("UPDATE INTERFACES");
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
            cellRowSpan = firstCell.getAttribute('rowspan');
        }
        let node = firstCell.getElementsByTagName('a')[0]
        if (node.text != msg.serverName) continue;
        
        //update interfaces if they exist
        if (cellRowSpan == null) continue;

        //get first interface name
        let interfaceCell = tableRows[i].getElementsByTagName('td')[INTERFACE_NAME];
        let interfaceStatusCell = tableRows[i].getElementsByTagName('td')[INTERFACE_STATUS];
        if (msg.interfaces[interfaceCell.innerHTML] == "Поднят") {
            interfaceStatusCell.style.color = "green";
        } else {
            interfaceStatusCell.style.color = "red";
        }
        interfaceStatusCell.innerHTML = msg.interfaces[interfaceCell.innerHTML]

        cellRowSpan--;
        i++;

        //other interfaces name will be in the first column due to rowspan attribute of other columns
        while (cellRowSpan > 0) {
            interfaceCell = tableRows[i].getElementsByTagName('td')[INTERFACE_NAME_SPAN];
            interfaceStatusCell = tableRows[i].getElementsByTagName('td')[INTERFACE_STATUS_SPAN];
            if (msg.interfaces[interfaceCell.innerHTML] == "Поднят") {
                interfaceStatusCell.style.color = "green";
            } else {
                interfaceStatusCell.style.color = "red";
            }
            interfaceStatusCell.innerHTML = msg.interfaces[interfaceCell.innerHTML]
            cellRowSpan--;
            i++;
        }
    }
}

function updateServerStateTable(server) {
    const SERVER_NAME = 0;
    const SERVER_STATE = 3;
    const INTERFACE_NAME = 4;
    const INTERFACE_NAME_SPAN = 0;
    
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
            cellRowSpan = firstCell.getAttribute('rowspan');
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

        //update interfaces if they exist
        if (cellRowSpan == null) continue;
        if (server.serverState != "Доступен") continue;

        //get first interface name
        let interfaces = {};
        interfaces['serverName'] = server.serverName;
        interfaces['interfaces'] = [];
        let interfaceCell = tableRows[i].getElementsByTagName('td')[INTERFACE_NAME];
        interfaces['interfaces'].push(interfaceCell.innerHTML);
        cellRowSpan--;
        i++;

        //other interfaces name will be in the first column due to rowspan attribute of other columns
        while (cellRowSpan > 0) {
            interfaceCell = tableRows[i].getElementsByTagName('td')[INTERFACE_NAME_SPAN];
            interfaces['interfaces'].push(interfaceCell.innerHTML);
            cellRowSpan--;
            i++;
        }
        socket.emit('updateInterfacesState', interfaces);
    }
}

function updateVMStateTable(vm) {
    const VM_NAME = 0;
    const VM_STATE = 4;
    
    let table = document.getElementById('vmTable'); 
    let tableRows = table.getElementsByTagName('tbody')[0].rows;
    for (let i = 0; i < tableRows.length; i++) {
        let firstCell = tableRows[i].getElementsByTagName('td')[VM_NAME];
        let node = firstCell.getElementsByTagName('a')[0]
        if (node.text != vm.vmName) continue;
        
        let stateCell = tableRows[i].getElementsByTagName('td')[VM_STATE];
        if (vm.vmState == "Доступна") {
            stateCell.style.color = "green";
        } else {
            stateCell.style.color = "red";
        }
        stateCell.innerHTML = vm.vmState
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
    socket.on('updatedInterfacesState', updateInterfaceTable);
    socket.on('updatedVMState', updateVMStateTable);

    updateServerState()
    updateVMState()
    //socket.emit('updateServerState', {dat: "1"});
    //console.log($servers)
});

