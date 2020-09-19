import asyncio
import concurrent.futures
import fabric
from app.stand.connections import conn_config

STAGES = [
    "Перезагрузка виртуальных машин (1/9)"
]

def restart_domain(vm):
    print("START RESTART DOMAIN")
    #from app.stand.connections import conn_config

    @fabric.task
    def restart_remote_domain(domain):
        print("Running command pwd")
        fabric.api.run('pwd')
        print("Trying to reset VM")
        if fabric.api.run('virsh reset {}'.format(domain)).failed:
            raise RuntimeError('Failed to reset VM!')

    @fabric.task
    def wait_remote_vm(c):
        with fabric.api.settings(
            connection_attempts=10,
            timeout=3,
        ):
            if fabric.api.run('uptime').failed:
                raise RuntimeError('Failed to connect VM!')

    #with fabric.api.hide('everything'):
    try:
        print("haha")
        print(vm.vmname)
        c = fabric.connection.Connection(host = vm.vmname, config = conn_config)
        #host, domain = vm_config.vm_allocation[vm]
        #print(vm_config.user_alias[host])
        print(c)
        c.run(restart_remote_domain)
        #fabric.api.execute(restart_remote_domain, domain, hosts=vm_config.user_alias[host])
        #fabric.api.execute(wait_remote_vm, hosts=vm_config.user_alias[vm])
    except SystemExit as e:
        print('Failed to restart domain! Wait_remote_vm')
        print(e)
        raise

def test(arg):
    print("test ")

class Runner:
    def __init__(self, test):
        self.tester = test


    def restart_vms(self):
        from app.models import VM
        try:
            vms = VM.query.all()
            self_args = [self for x in vms]
            with concurrent.futures.ThreadPoolExecutor(len(vms)) as executor:
                #executor.map(restart_domain, vms)
                #executor.map(test, vms)
                restart_domain(vms[0])
        except BaseException as e:
            print('Failed to restart vms!')
            print(e)
            raise
        print("finished")


    def run(self, exp):
        self.restart_vms()

class Tester:
    queue = list()

    def __init__(self):
        from app.models import Experiment
        exps = Experiment.query.filter_by(completed = False).all()

        #TODO: sorting
        self.queue = exps

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

    async def run_experiments(self):
        print("Async run of run")
        self.current_experiment = self.queue[0]
        self.current_stage = STAGES[0]
        self.runner.run(self.current_experiment)
        pass

    def start(self):
        if not self.running:
            self.running = True
            
            #add backward compatibility with python 3.5
            #TODO check loops
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.run_experiments())

