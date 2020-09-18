"use strict"

let socket = null;

function updateTesterStateTable(msg) {
    let a = document.getElementById('curr_exp_id');
    a.href = '/experiment/' + msg.current_experiment;
    a.text = msg.current_experiment;

    let stage = document.getElementById('exp_stage');
    stage.innerHTML = msg.current_stage;
    console.log("Received new tester state");

}

// Client Side Javascript to receive server and interface state.
$(document).ready(function(){
    // start up the SocketIO connection to the server - the namespace 'test' is also included here if necessary
    socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    // this is a callback that triggers when the "my response" event is emitted by the server.
    socket.on('updatedTesterState', updateTesterStateTable);
    //socket.on('updatedInterfacesState', updateInterfaceTable);
    //socket.on('updatedVMState', updateVMStateTable);

    socket.emit('updateTesterState', {});
    //socket.emit('updateServerState', {dat: "1"});
    //console.log($servers)
});

