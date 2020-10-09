import asyncio
import concurrent.futures
import fabric
from app.stand.connections import conn_config

STAGES = [
    "Перезагрузка виртуальных машин (1/9)",
    "Эксперимент завершился успешно"
]

RUN_TIMEOUT = 20
RESTART_VMS_TIMEOUT = 50

def restart_domain(vm):
    from app.models import Server

    def restart_remote_domain(c, domain):
        if c.run('virsh reset {}'.format(domain), hide = True).failed:
            raise RuntimeError('Failed to reset VM!')

    def wait_remote_vm(c):
        while True:
            try:
                if not(c.run('uptime', hide=True).failed):
                    return
            except BaseException as e:
                print(e)

    try:
        servername = Server.query.filter_by(id = vm.server_id).all()[0].servername
        c_server = fabric.connection.Connection(host = servername, config = conn_config)
        c_client = fabric.connection.Connection(host = vm.vmname, config = conn_config, connect_timeout = 0)

        restart_remote_domain(c_server, vm.vmname)
    except SystemExit as e:
        print('Failed to restart domain! Wait_remote_vm')
        print(e)
        raise

def wait_domain(vm):
    from app.models import Server

    def wait_remote_vm(c):
        while True:
            try:
                if not(c.run('uptime', hide=True).failed):
                    return
            except BaseException as e:
                pass
                #print(e)

    try:
        servername = Server.query.filter_by(id = vm.server_id).all()[0].servername
        c_server = fabric.connection.Connection(host = servername, config = conn_config)
        c_client = fabric.connection.Connection(host = vm.vmname, config = conn_config, connect_timeout = 0)

        wait_remote_vm(c_client)
    except SystemExit as e:
        print('Failed to restart domain! Wait_remote_vm')
        print(e)
        raise


def stop_process_pool(executor):
    for pid, process in executor._processes.items():
        process.terminate()
    executor.shutdown()


class Runner:
    def __init__(self, test):
        self.tester = test
        self.current_stage = 0

    def update_stage(self):
        self.current_stage += 1
        self.tester.current_stage = STAGES[self.current_stage]
        self.tester.send_state_update()


    def restart_vms(self, exp):
        from app.models import VM

        try:
            vms = VM.query.all()
            self_args = [self for x in vms]
            #TODO make parallel
            for vm in vms:
                restart_domain(vm)
            for vm in vms:
                wait_domain(vm)

            #deprecated parallel code
            #with concurrent.futures.ProcessPoolExecutor(len(vms)) as executor:
            #    try:
            #        for future in concurrent.futures.as_completed(executor.map(restart_domain, vms, timeout=RESTART_VMS_TIMEOUT), timeout=RESTART_VMS_TIMEOUT):
            #            future.result(timeout=RESTART_VMS_TIMEOUT)
            #    except concurrent.futures._base.TimeoutError:
            #        print("TIMEOUT ERROR")
            #        stop_process_pool(executor)
        except BaseException as e:
            print('Failed to restart vms!')
            print(e)
            raise

    stages = [
        restart_vms,
        ]


    def run(self, exp):
        self.current_stage = 0
        self.tester.current_stage = STAGES[self.current_stage]
        self.tester.send_state_update()

        for stage in self.stages:
            stage(self, exp)
            self.update_stage()

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
        import threading
        import multiprocessing
        print("Async run of run")
        while self.queue:
                self.current_experiment = self.queue.pop(0)
                self.current_stage = STAGES[0]
                #exp_thread = threading.Thread(target = self.runner.run, args = (self.current_experiment, ))
                exp_thread = multiprocessing.Process(target = self.runner.run, args = (self.current_experiment, ))
                exp_thread.start() 
                exp_thread.join(timeout = RUN_TIMEOUT)
                if exp_thread.is_alive():
                    print("EXIT of EXPERIMENT due to TIMEOUT")
                    exp_thread.terminate()
                print("Len of queue: {}".format(len(self.queue)))
                # for DEBUG
                break

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


