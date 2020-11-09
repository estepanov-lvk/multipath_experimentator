"use strict"

let socket = null;
let exp_socket = null;

function updateTesterStateTable(msg) {
    let a = document.getElementById('curr_exp_id');
    a.href = '/experiment/' + msg.current_experiment;
    a.text = msg.current_experiment;

    let stage = document.getElementById('exp_stage');
    stage.innerHTML = msg.current_stage;
    console.log("Received new tester state");

}

function updateExperimentState(msg) {
    console.log("Received experiment state")
    console.log(msg.current_stage)
    let a = document.getElementById('curr_exp_id');
    a.href = '/experiment/' + msg.current_experiment;
    a.text = msg.current_experiment;

    let stage = document.getElementById('exp_stage');
    stage.innerHTML = msg.current_stage;
}

// Client Side Javascript to receive server and interface state.
$(document).ready(function(){
    // start up the SocketIO connection to the server - the namespace 'test' is also included here if necessary
    socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    exp_socket = io.connect('http://' + document.domain + ':' + location.port + '/experiment_state');
    // this is a callback that triggers when the "my response" event is emitted by the server.
    socket.on('updatedTesterState', updateTesterStateTable);
    exp_socket.on('msg', updateExperimentState);
    exp_socket.emit('update', {});
    //socket.on('updatedInterfacesState', updateInterfaceTable);
    //socket.on('updatedVMState', updateVMStateTable);

    socket.emit('updateTesterState', {});
    //socket.emit('updateServerState', {dat: "1"});
    //console.log($servers)
});

