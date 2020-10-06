import asyncio
import concurrent.futures
import fabric
from app.stand.connections import conn_config

STAGES = [
    "Перезагрузка виртуальных машин (1/9)"
]

def restart_domain(vm):
    from app.models import Server

    def restart_remote_domain(c, domain):
        if c.run('virsh reset {}'.format(domain)).failed:
            raise RuntimeError('Failed to reset VM!')

    def wait_remote_vm(c):
        c.run('uptime')

    try:
        servername = Server.query.filter_by(id = vm.server_id).all()[0].servername
        c_server = fabric.connection.Connection(host = servername, config = conn_config)
        c_client = fabric.connection.Connection(host = vm.vmname, config = conn_config, connect_timeout = 0)

        restart_remote_domain(c_server, vm.vmname)
        wait_remote_vm(c_client)
    except SystemExit as e:
        print('Failed to restart domain! Wait_remote_vm')
        print(e)
        raise

class Runner:
    def __init__(self, test):
        self.tester = test


    def restart_vms(self):
        from app.models import VM

        self.tester.current_stage = STAGES[0]
        self.tester.send_state_update()
        try:
            vms = VM.query.all()
            self_args = [self for x in vms]
            with concurrent.futures.ThreadPoolExecutor(len(vms)) as executor:
                res = executor.map(restart_domain, vms)
                res = list(res)
        except BaseException as e:
            print('Failed to restart vms!')
            print(e)
            raise
        print("finished")


    def run(self, exp):
        self.restart_vms()
        self.tester.send_state_update()

class Tester:
    queue = list()

    def __init__(self):
        from app.models import Experiment
        from app import socketio

        exps = Experiment.query.filter_by(completed = False).all()

        #TODO: sorting
        self.queue = exps
        self.socketio = socketio

        @self.socketio.on('update', namespace='/experiment_state')
        def updateExperimentState(msg):
            self.socketio.emit('msg', self.form_state(), namespace='/experiment_state')
            print("Update Experiment STATE !!!!!!!!!!!!!!!!!")

        self.running = False
        self.current_experiment = -1
        self.current_stage = "Выключен"

        self.runner = Runner(self)

    def waiting_experiments(self):
        return self.queue
        
    def form_state(self):
        state_msg = {}
        state_msg['current_experiment'] = self.current_experiment.id
        state_msg['current_stage'] = self.current_stage
        return state_msg

    def send_state_update(self):
        from flask_socketio import emit
        #self.socketio.emit(self.form_state(), namespace='/experiment_state')
        self.socketio.emit('msg', self.form_state(), namespace='/experiment_state')
        #emit('update', self.form_state(), broadcast=True, include_self=False)

    async def run_experiments(self):
        print("Async run of run")
        self.current_experiment = self.queue[0]
        self.current_stage = STAGES[0]
        self.runner.run(self.current_experiment)

    def start_in_thread(self, loop):
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.run_experiments())

    def start(self):
        if not self.running:
            self.running = True
            
            #add backward compatibility with python 3.5
            #TODO check loops
            loop = asyncio.new_event_loop()
            
            import threading
            t = threading.Thread(target = self.start_in_thread, args = (loop, ))
            t.start()


