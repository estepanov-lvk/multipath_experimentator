import asyncio
import concurrent.futures
import fabric
from app.stand.connections import conn_config
import numpy
import pickle
import json
import networkx

STAGES = [
    "Перезагрузка виртуальных машин (1/9)",
    "Очистка топологии (2/9)",
    "Разворачивание топологии (3/9)",
    "Ожидание старта виртуальных машин (4/9)",
    "Настройка виртуальных машин (5/9)",
    "Очистка старых результатов (6/9)",
    "Старт сбора статистики (7/9)",
    "Запуск потоков (8/9)",
    "Сбор результатов (9/9)",
    "Эксперимент завершился успешно"
]

RUN_TIMEOUT = 2000
RESTART_VMS_TIMEOUT = 50

#TODO move IFMAP to models

BORDER_SWITCH = 1234
IF_MAP = { #interfaces on head to loaders 
    'olya_at_vm_fdmp': 'ens8',		# format ??
    'olya_at_vm_fdmp2': 'ens9',
    #'fdmp_at_w1loader3-clone': 'enp15s0f1',
    #'fdmp_at_w1loader4': 'enp15s0f1',
    #'fdmp_at_w4loader1-clone': 'enp8s0f0',
    #'fdmp_at_w4loader2-clone': 'enp131s0f0',
    #'fdmp_at_w4loader3-clone': 'enp131s0f1',
    #'fdmp_at_w4loader4': 'enp15s0f0',
}

USER_MAP = {
    "head": 'olya',
    #"w1": 'arccn',
    "w2": 'fdmp',
    "vm_fdmp": 'olya',
    "vm_fdmp2": 'olya',
    #"w1loader3-clone": 'fdmp',
    #"w1loader4": 'fdmp',
    #"w4loader1-clone": 'fdmp',
    #"w4loader2-clone": 'fdmp',
    #"w4loader3-clone": 'fdmp',
    #"w4loader4": 'fdmp',
}

NAME_MAP = {
    'head' : 'head',
    'loader1' : 'vm_fdmp',
    'loader2' : 'vm_fdmp2',
    'user' : 'olya',
}



# head - where topology is
# w1, w2, ..., w4 - where loaders are
# loader1, ... - VM for load
class VMConfig(object):
    def __init__(self):
        self.hosts = {
            'head': '192.168.122.3',

            #'w1': '172.30.2.11',
            'w2': '172.30.2.12',

            'vm_fdmp': '192.168.122.227',
            'vm_fdmp2': '192.168.122.238',
            #'w1loader3-clone': '172.30.2.113',
            #'w1loader4': '172.30.2.114',
            #'w4loader1-clone': '172.30.2.141',
            #'w4loader2-clone': '172.30.2.142',
            #'w4loader3-clone': '172.30.2.143',
            #'w4loader4': '172.30.2.144',
        }
        self.vm_allocation = {
            'vm_fdmp': ['w2', 'vm_fdmp'], #or is it username?
            'vm_fdmp2': ['w2', 'vm_fdmp2'],
            #'w1loader3-clone': ['w1', 'w1loader3-clone'],
            #'w1loader4': ['w1', 'w1loader4'],
            #'w4loader1-clone': ['w4', 'w4loader1-clone'],
            #'w4loader2-clone': ['w4', 'w4loader2-clone'],
            #'w4loader3-clone': ['w4', 'w4loader3-clone'],
            #'w4loader4': ['w4', 'w4loader4'],
            
            
        }
        self.vm_data_if = {
            'vm_fdmp': ['ens8', '10.1.1.1'],
            #'w4loader1-clone': ['ens9', '10.1.1.2'],
            'vm_fdmp2': ['ens8', '10.1.1.2'],
            #'w4loader2-clone': ['ens9', '10.2.1.2'],
            #'w1loader3-clone': ['ens9', '10.3.1.1'],
            #'w4loader3-clone': ['ens9', '10.3.1.2'],
            #'w1loader4': ['ens9', '10.4.1.1'],
            #'w4loader4': ['ens9', '10.4.1.2'],
            
            
        }
        self.vm_qos_classes = {
            133 : ['vm_fdmp'], #kbps
            #1200 : ['w4loader1-clone'],
            500 : ['vm_fdmp2'],
            #2750 : ['w4loader2-clone'],
            #800 : ['w1loader3-clone'],
            #5000 : ['w4loader3-clone'],
        }
        self.vm_flow_share = {
            'vm_fdmp' : 0.01, # <144p
            'vm_fdmp2' : 0.1, # 144-240p
            #'w1loader3-clone' : 0.1, # 240-360p
            #'w4loader1-clone' : 0.2, # 360-480p
            #'w4loader2-clone' : 0.4, # 480-720p
            #'w4loader3-clone' : 0.2  # >720p
        }
        self.vm_transfer_size = {
            41562500 : ['vm_fdmp'],
            156250000 : ['vm_fdmp2'],
            #250000000 : ['w1loader3-clone'],
            #375000000 : ['w4loader1-clone'],
            #859375000 : ['w4loader2-clone'],
            #1562500000 : ['w4loader3-clone'],
            #100000000 : ['w1loader1-clone', 'w4loader1-clone'],
            #100000000 : ['w1loader2-clone', 'w4loader2-clone'],
            #100000000 : ['w1loader3-clone', 'w4loader3-clone'],
        }
        self.vm_bitrate = {
            'vm_fdmp': 133000, 
            'vm_fdmp2': 500000,
            #'w1loader3-clone': 800000,
            #'w4loader1-clone': 1200000,
            #'w4loader2-clone': 2750000, #bits/sec
            #'w4loader3-clone': 5000000,
        }
        self.username = USER_MAP
        self.user_alias = {x: '{}_at_{}'.format(self.username[x], x) for x in self.hosts.keys()}
        self.root_alias = {x: 'root_at_{}'.format(x) for x in self.hosts.keys()}

    def make_ssh_config(self, filename):
        entries = []
        for host, ip in sorted(self.hosts.items()):
            host_status = 'vm' if host in self.vm_allocation else 'server'
            identity = '~/.ssh/fdmp/{}@{}'.format(self.username[host], host)
            entries.append((self.user_alias[host], ip, self.username[host], identity))
            identity = '~/.ssh/fdmp/root@{}'.format(host)
            entries.append((self.root_alias[host], ip, 'root', identity))

        with open(filename, 'wt') as fd:
            for x in entries:
                fd.write(
                    textwrap.dedent("""
                        Host {}
                            Hostname {}
                            User {}
                            IdentityFile {}
                    """).format(*x)
                )


vm_config = VMConfig()

def get_qos_classes():
    #TODO not to rely on the vm_config (we should use database)
    classes = []
    for cl in sorted(vm_config.vm_qos_classes.keys()):
        vm_name = vm_config.vm_qos_classes[cl][0]
        new_class = {}
        new_class['name'] = cl
        new_class['vm'] = vm_name
        new_class['bitrate'] = vm_config.vm_bitrate[vm_name]
        new_class['volume'] = [key for key in vm_config.vm_transfer_size if vm_name in vm_config.vm_transfer_size[key]][0] 
        new_class['share'] = vm_config.vm_flow_share[vm_name]
        classes.append(new_class)
    return classes

def genNormal(duration, subflows, seed):
    numpy.random.seed(seed)
    mu, sigma = duration/2, 10
    s = numpy.random.normal(mu, sigma, subflows)
    difference = max(s) + 3
    coef = duration / difference
    newList = []
    for elem in s:
        newList.append(elem * coef)
    return newList

def genWeibull(duration, subflows, seed):
    a = 5.
    numpy.random.seed(seed)
    s = numpy.random.weibull(a, subflows)
    difference = max(s) + 3
    coef = duration / difference
    newList = []
    for elem in s:
        newList.append(elem * coef)
    return newList

def genUniform(duration, subflows, seed):
    numpy.random.seed(seed)
    s = numpy.random.uniform(0.0, duration, subflows)
    difference = max(s) + 3
    coef = duration / difference
    newList = []
    for elem in s:
        newList.append(elem * coef)
    return newList

def genStatic(subflows):
    s = []
    for i in range(subflows):
        s.append(0.0)
    return s


def getDistr(distr, duration, subflows, seed):
    resultArray = []
    if (distr.lower() == "normal"):
        resultArray = genNormal(duration, subflows, seed)
    elif (distr.lower() == "weibull"):
        resultArray = genWeibull(duration, subflows, seed)
    elif (distr.lower() == "uniform"):
        resultArray = genUniform(duration, subflows, seed)
    elif (distr.lower() == "static"):
        resultArray = genStatic(subflows)
    return resultArray

'''
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
'''

def restart_domain(vm):
    #@fabric.api.task
    def restart_remote_domain(domain):
        print("Running command pwd")
        fabric.connection.Connection('127.0.0.1').run('pwd')
        print("Trying to reset VM")
        if fabric.connection.Connection('127.0.0.1').run('virsh reset {}'.format(domain)).failed:
            raise RuntimeError('Failed to reset VM!')

    #@fabric.api.task
    def wait_remote_vm():
        with fabric.api.settings(
            connection_attempts=10,
            timeout=3,
        ):
            if fabric.connection.Connection('127.0.0.1').run('uptime').failed:
                raise RuntimeError('Failed to connect VM!')

    #with fabric.api.hide('everything'):
    try:
        host, domain = vm_config.vm_allocation[vm]
        print(vm_config.user_alias[host])
	
        #fabric.connection.Connection('127.0.0.1').execute(restart_remote_domain, domain, hosts=vm_config.user_alias[host])
        #fabric.api.execute(wait_remote_vm, hosts=vm_config.user_alias[vm])
	restart_remote_domain(domain)
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

def start_topology(exp):
    model = ''
    subnum = exp.subflow
    topo = "topo/" + exp.topo
    active = '--active {} {}'.format(exp.poles, exp.poles_seed)
    #TODO check parameters
    if exp.model in ['mcmf', 'gspf']:
        model = '--sliced {} --rules_dump {}_rules.dump'.format(
                    subnum,
                    exp.model)
    else:
        model = '--ecmp {}'.format(exp.model)

    from app.models import Server

    head = Server.query.filter_by(servername = 'head').all()[0]
    head_user = head.username
    #TODO: make topology on right user
    head_user = 'fdmp'
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    if head_c.run('sudo -H bash -c "cd /home/{}/netbuilder; ./run_1st.py -b {} {} {}"'.format(
                    head_user,
                    topo,
                    active,
                    model)).failed:
        raise RuntimeError('Failed on run 1st!')

def set_qos(exp):
    from app.models import Server
    #TODO make it in config or parameters of experiment
    RATE = 1000 #Mbps
    RTT = 2 #ms

    head = Server.query.filter_by(servername = 'head').all()[0]
    head_user = head.username
    #TODO: make topology on right user
    head_user = 'fdmp'
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    if head_c.run('sudo -H bash -c "cd /home/{}/netbuilder; ./set_qos.py --link_opts rate={},loss=10,rtt={},jitter=0"'.format(
                    head_user, RATE, RTT)).failed:
        raise RuntimeError('Failed on set qos')

def setup_multiloader(loader_pairs, exp):
    import io
    subnum = exp.subflow
    result_config = '{{\n"subnum": {},\n"connections":[\n'.format(subnum)
    for loader in loader_pairs:
            result_config += '{{\n\t\t"client_ports": "{}-{}",\n'\
                                '\t\t"client_if": "{}",\n'\
                                '\t\t"server_if": "{}",\n'\
                                '\t\t"server_ip": "{}"\n'\
                                '}},\n'.format(loader['client_ports'], 
                                            loader['client_ports'] + loader['client_flows'] - 1,
                                            IF_MAP[loader['remote_client_name']],
                                            IF_MAP[loader['remote_server_name']],
                                            loader['server_ip'])
    result_config = result_config[:-2]
    result_config += '\n]\n}\n'

    active = '--active {} {}'.format(exp.poles, exp.poles_seed)
    head_user = 'fdmp'
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    head_c.put(io.StringIO(result_config), remote='/home/{}/netbuilder/testbed.json'.format(head_user))
        
    if head_c.run('sudo -H bash -c "cd /home/{}/netbuilder; ./multiloader.py {} net.dump {} {}"'.format(head_user, active, BORDER_SWITCH, exp.routes_seed)).failed:
        raise RuntimeError('Failed on multiloader')


#TODO make normal QoS
def set_bitrate_in_json():
    print("TEST1")

    with open("route_config.json") as f:
        dump = json.load(f)
    #qos_list = dump["qos"]
    print("TEST2")
    new_qos_list = []
    for vm_name in vm_config.vm_bitrate:
        print("vm_name=" + vm_name)
        num1 = vm_name[1]
        num2 = vm_name[8]
        ip = "10." + str(num1) + ".1." + str(num2)
        for qos_dict in dump['stand-data']['qos']:
            if qos_dict["s_ip"] == ip:
                qos_dict["bw"] = vm_config.vm_bitrate[vm_name] * 0.001
                new_qos_list.append(qos_dict)

    dump["stand-data"]["qos"] = new_qos_list
    print("TEST3") 
    with open("route_config.json", 'w') as outfile:
        #json.dump(dump, outfile)
        outfile.write(json.dumps(dump))
    print(dump)




def create_controller_config(topo, subflow, poles, proto):
    BANDWIDTH = 1000000 #Kbit/s  current value is 1 Gbit/s
    print(topo, subflow, poles)
    dict1 = {}
    dict1["name"] = "stand-data"
    dict1["rest"] = False
    dict1["cli"] = False
    dict1["sub_num"] = subflow
    dict1["seed"] = 1
    dict1["pole_ratio"] = poles
    dict1["protocol"] = proto
    dict_topo = {}
    dict_topo["name"] = topo
    dict_edges = {}
    list_edges = []
    with open("/home/fdmp/netbuilder/topo/" + topo, 'rb') as fp:
        graph = pickle.load(fp)
    
    edges = graph.edges()
    edges_filtered = []
    for t in edges:
        if not t in edges_filtered:
            edges_filtered.append(t)
    for t in edges_filtered:
        dict_edge = {}
        dict_edge["s_node"] = t[0]
        dict_edge["d_node"] = t[1]
        dict_edge["bw"] = BANDWIDTH
        list_edges.append(dict_edge)
        dict_edge = {}
        dict_edge["s_node"] = t[1]
        dict_edge["d_node"] = t[0]
        dict_edge["bw"] = BANDWIDTH
        list_edges.append(dict_edge)
    dict_topo["nodes"] = graph.nodes()
    dict_topo["edges"] = list_edges
    dict1["topo"] = dict_topo
    list_qos = []
    for n in range(1, 4):
        dict_qos = {}
        src = "10." + str(n) + ".1.1"
        dst = "10." + str(n) + ".1.2"
        dict_qos["s_ip"] = src
        dict_qos["d_ip"] = dst
        list_qos.append(dict_qos)
        dict_qos = {}
        dict_qos["s_ip"] = dst
        dict_qos["d_ip"] = src
        list_qos.append(dict_qos)
    dict1["qos"] = list_qos
    str1 = '{ "services": [ "of-server", "of-server-cli", "of-server-rest", "controller", "switch-manager", "switch-manager-cli", "switch-manager-rest", "switch-ordering", "link-discovery", "link-discovery-cli", "link-discovery-rest", "recovery-manager", "recovery-manager-rest", "flow-entries-verifier", "ofmsg-sender", "stats-rules-manager", "stats-rules-manager-rest", "topology", "topology-rest", "stats-bucket-rest", "dpid-checker", "database-connector", "flow-table-rest", "group-table-rest", "meter-table-rest", "aux-devices-rest", "stand-data" ], "flow-entries-verifier": { "active": false, "poll-interval": 30000 }, "dpid-checker": { "dpid-format": "dec", "AR": [ "1", "2", "3" ], "DR": [ "1234", "4", "5", "6" ] }, "recovery-manager": { "id": 1, "status": "backup", "hb-mode": "unicast", "hb-address-primary": "127.0.0.1", "hb-port-primary": 1234, "hb-address-backup": "127.0.0.1", "hb-port-backup": 1237, "hb-port-broadcast": 50000, "hb-address-multicast": "239.255.43.21", "hb-port-multicast": 50000, "hb-interval": 200, "hb-primaryDeadInterval": 800, "hb-backupDeadInterval": 1000, "hb-primaryWaitingInterval": 600 }, "database-connector": { "db-type": "redis", "db-address": "127.0.0.1", "db-port": 6379, "db-pswd": "" }, "link-discovery": { "queue": 1, "poll-interval": 5 }, "of-server": { "address": "0.0.0.0", "port": 6653, "nthreads": 4, "echo-interval": 5, "echo-attempts": 3, "secure": false }, "rest-listener": { "address": "0.0.0.0", "port": "8000" }, "stand-data": ' + json.dumps(dict1) + "}"
    with open('route_config.json', 'w') as outfile:
        try:
            outfile.write(str1)
        except Exception as e:
            print("Exception! " + e)



def start_controller(exp):
    create_controller_config(exp.topo, exp.subflow, exp.poles, exp.protocol)
    set_bitrate_in_json()
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)

    head_c.put('route_config.json', '/home/arccn/runos/runos-settings.json')

    controller_command = 'cd /home/arccn/runos; tmux new -d \\"source ~/.nix-profile/etc/profile.d/nix.sh; nix-shell --command build/runos\\"'
    if head_c.run('bash -c "{}"'.format(controller_command)).failed:
        raise RuntimeError('Failed on runos start')

def kill_controller(exp):
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    if head_c.run('bash -c "pkill runos"').failed:
        raise RuntimeError('Failed to kill controller process!')

def start_watch(exp):
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    #TODO check that script is on the head (beforehand)

    if head_c.run('bash -c "/home/arccn/watch_script.sh"').failed:
        raise RuntimeError('Failed on watch start')

def kill_watch(exp):
    SWITCH = 1234 #TODO add switch from experiment parameters
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    if head_c.run(str('''bash -c "pkill -f 'watch -n 1 sudo ovs-ofctl dump-flows -O openflow13 {} >> {}_result.txt'"'''.format(SWITCH, SWITCH))).failed:
        raise RuntimeError('Failed to kill watch process')

def setup_loader(exp, vm):
    def setup_interface(vm_c, iface, ip, subnum):
        vm_c.run('sudo -H bash -c "ifconfig {} down"'.format(iface))
        vm_c.run('sudo -H bash -c "ip addr flush dev {}"'.format(iface))
        for i in range(subnum):
            new_ip = ip.split('.')
            new_ip[2] = str(i + 1)
            new_ip = '.'.join(new_ip)

            if vm_c.run('sudo -H bash -c "ip addr add {}/24 dev {}"'.format(new_ip, iface)).failed:
                raise RuntimeError('Failed to assign address to interface!')

        if vm_c.run('sudo -H bash -c "ifconfig {} txqueuelen 8000"'.format(iface)).failed:
            raise RuntimeError('Failed to tune txqueuelen')
        if vm_c.run('sudo -H bash -c "ifconfig {} up"'.format(iface)).failed:
            raise RuntimeError('Failed to set up interface!')
        if vm_c.run('sudo -H bash -c "tc qdisc replace dev {} root handle 1: fq limit 400000"'.format(iface)).failed:
            raise RuntimeError('Failed to set up tc')
        return

    def setup_multipath(vm_c, mp):
        if vm_c.run('sudo -H bash -c "sysctl -w net.mptcp.mptcp_enabled={}"'.format(mp)).failed:
            raise RuntimeError('Failed to enable MPTCP!')
        if vm_c.run('sudo -H bash -c "sysctl -w net.mptcp.mptcp_debug=1"').failed:
            raise RuntimeError('Failed to enable MPTCP debug')
        tcp_mem = "sysctl -w net.ipv4.tcp_mem='16777216 16777216 16777216'"
        if vm_c.run('sudo -H bash -c "{}"'.format(tcp_mem)).failed:
            raise RuntimeError('Failed to tune tcp_mem')
        if vm_c.run('sudo -H bash -c "sysctl -w net.ipv4.tcp_syncookies=0"').failed:
            raise RuntimeError('Failed to tune syn cookies')
        if vm_c.run('sudo -H bash -c "sysctl -w net.ipv4.tcp_max_syn_backlog=1024"').failed:
            raise RuntimeError('Failed to tune tcp_max_syn_backlog')
        if vm_c.run('sudo -H bash -c "sysctl -w net.core.somaxconn=1024"').failed:
            raise RuntimeError('Failed to tune net.core.sorted')
        if vm_c.run('sudo -H bash -c "sysctl -w net.ipv4.tcp_syn_retries=6"').failed:
            raise RuntimeError('Failed to set up tcp syn_retries')
        if vm_c.run('sudo -H bash -c "sysctl -w net.mptcp.mptcp_syn_retries=5"').failed:
            raise RuntimeError('Failed to set up mptcp syn_retries')

    def setup_cc(vm_c, cc):
        if vm_c.run('sudo -H bash -c "sysctl -w net.ipv4.tcp_congestion_control={}"'.format(cc)).failed:
            raise RuntimeError('Failed to configure congestion control!')

    #TODO interfaces
    iface, ip = vm_config.vm_data_if[vm.vmname]
    subnum = exp.subflow
    #TODO root? 
    vm_c = fabric.connection.Connection(host = vm.vmname, config = conn_config)

    try: 
        # with head_c.hide('everything'):
        setup_interface(vm_c, iface, ip, subnum)
        setup_multipath(vm_c, int(exp.mode == 'mp'))
        setup_cc(vm_c, exp.cc)
    except SystemExit as e:
        print("Failed to configure vm")
        print(e)
        raise

def collect_collectd_results(result_directory):
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    try:
        if head_c.run('pkill -HUP --pidfile ~/collectd.pid').failed:
            raise RuntimeError('Failed to stop collectd!')
        if head_c.run('tar -czf csv.tar.gz /home/fdmp/csv').failed:
            raise RuntimeError('Failed to archive collectd results!')
        head_c.get('csv.tar.gz', '{}/csv.tar.gz'.format(result_directory))
        if head_c.run('rm -rf /home/fdmp/csv').failed:
            raise RuntimeError('Failed to remove collected data directory!')
        if head_c.run('rm -rf csv.tar.gz').failed:
            raise RuntimeError('Failed to remove collected data archive!')
    except SystemExit as e:
        print("Failed to collect results")
        print(e)
        raise


def collect_controller_results(result_directory):
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    try:
        head_c.get('runos/result.txt', '{}/runos_result.txt'.format(result_directory))
        if head_c.run('rm -f runos/result.txt').failed:
            raise RuntimeError('Failed to remove runos result file!')
    except SystemExit as e:
        print("Failed to collect results from runos controller")
        print(e)
        raise

def collect_watch_results(result_directory):
    SWITCH = 1234 #TODO make from experiment config
    head_c = fabric.connection.Connection(host = 'head', config = conn_config)
    try:
        head_c.get('{}_result.txt'.format(SWITCH), '{}/{}_result.txt'.format(result_directory, SWITCH))
        if head_c.run('rm -f {}_result.txt'.format(SWITCH)).failed:
            raise RuntimeError('Faile to remove watch result file!')
    except SystemExit as e:
        print('Failed to collect results from watch process')
        print(e)
        raise



def collect_iperf3_results(result_directory, loader_pairs):
    def collect_remote_iperf3_results(result_directory, vmname):
        from pathlib import Path
        vm_c = fabric.connection.Connection(host = vmname, config = conn_config)
        if vm_c.run('tar -czf iperf3.tar.gz iperf3').failed:
            raise RuntimeError('Failed to archive iperf3 results!')
        Path('{}/iperf'.format(result_directory)).mkdir(parents=True, exist_ok=True)
        vm_c.get('iperf3.tar.gz', '{}/iperf/{}.tar.gz'.format(result_directory, vmname))
        if vm_c.run('rm -rf iperf*').failed:
            raise RuntimeError('Failed to remove collected data!')

    servers = set(x['remote_server_name'] for x in loader_pairs)
    clients = set(x['remote_client_name'] for x in loader_pairs)
    hosts=list(servers | clients)
    try:
        for host in hosts:
            collect_remote_iperf3_results(result_directory, host.split('_')[-1])
    except SystemExit as e:
        print("Failed to collect results")
        print(e)
        raise



def setLoaderQos(subflows, protocol):
    from app.models import VM

    def modifyQos(vm_c, qos):
        if vm_c.run('sudo -H bash -c "echo {} > /proc/sys/net/fdmp/qos_req_default"'.format(qos)).failed:
            raise RuntimeError("Failed to modify qos!")
    
    def modifyPathManager(vm_c):
        if vm_c.run('sudo -H bash -c "echo default > /proc/sys/net/mptcp/mptcp_path_manager"').failed:
            raise RuntimeError("Failed to modify path manager!")
    def setPathManagerToMptcp(vm_c):
        if vm_c.run('sudo -H bash -c "echo ndiffports > /proc/sys/net/mptcp/mptcp_path_manager"').failed:
            raise RuntimeError("Failed to set path to mptcp!")

    def setSubflows(vm_c, subflows):
        if vm_c.run('sudo -H bash -c "' + 'echo ' + str(subflows) + ' > /proc/sys/net/fdmp/fdmp_subflows_num"').failed:
            raise RuntimeError("Failed to modify subflow number!")
    def disableFdmp(vm_c):
        if vm_c.run('sudo -H bash -c "echo 0 > /proc/sys/net/fdmp/fdmp_enabled"').failed:
            raise RuntimeError("Failed to disable fdmp!")
    def enableFdmp(vm_c):
        if vm_c.run('sudo -H bash -c "echo 1 > /proc/sys/net/fdmp/fdmp_enabled"').failed:
            raise RuntimeError("failed to enable fdmp!")
    
    for key in vm_config.vm_qos_classes:
        print(key)
        for loader_name in vm_config.vm_qos_classes[key]:
            #print("key = " + key + " loader name=" + loader_name)
            vm_c = fabric.connection.Connection(host = loader_name, config = conn_config)
            try:
                if protocol == 'fdmp':
                    print("PROTOCOL = FDMP")
                    modifyQos(vm_c, (int)(key * 0.9)) #90% from application rate
                    modifyPathManager(vm_c)
                    setSubflows(vm_c, subflows)
                    enableFdmp(vm_c)
                elif protocol == 'mptcp':
                    print("PROTOCOL = MPTCP")
                    setPathManagerToMptcp(vm_c)
                    disableFdmp(vm_c)
            except SystemExit as e:
                print("Failed to execute modify qos!")
                raise


def start_iperf3_servers(params):
    import textwrap
    vm_c = fabric.connection.Connection(host = params['remote_server_name'].split('_')[-1], config = conn_config)
    vm_c.run(' '.join(
            textwrap.dedent('''
                parallel
                --no-notice
                --xapply
                --files
                --results iperf3
                --max-procs {job_number}
                
                /usr/local/bin/iperf3
                --server
                --bind {server_ip}
                --port {{1}}
                --one-off
                --json
                
                
                ::: {server_ports}
            ''').splitlines()
            ).format(
                job_number=len(params['server_ports']),
                server_ip=params['server_ip'],
                server_ports=' '.join(map(str, params['server_ports'])),
            )
    )


def send_distribution_files(vm_c, exp, params):
    import io
    for flow_num,seed,p_id in zip(params['client_flows'], params['distrSeed'], params['id']):
        distrLines = ""
        distrString = ""
        flow_start_time = getDistr(exp.distribution, exp.time, exp.flows, seed)
        for i in range(flow_num):
            distrString += str(int(flow_start_time[i])) + " "
        distrLines = str(exp.flows) + "\n" + distrString;
        vm_c.put(io.StringIO(distrLines), 'distrFile{}.txt'.format(p_id))
        print(distrLines)

def start_iperf3_clients(params, exp):
        import textwrap
        import math
        vm_c = fabric.connection.Connection(host = params['remote_client_name'].split('_')[-1], config = conn_config)
         
        print("load_flow_number=", str(exp.flows),  " kwargs client flows = ", str(params['client_flows']))
        send_distribution_files(vm_c, exp, params)
        
        #QoS setup
        client_name = params['remote_client_name']
        transfer_str = ""
        for key in vm_config.vm_transfer_size:
            for vm_name in vm_config.vm_transfer_size[key]:
                if client_name.find(vm_name) != -1:
                    transfer_str = str(key) #+ "GB"
        if transfer_str == "":
            transfer_str = "100000000"
        bitrate = ""
        for vm_name in vm_config.vm_bitrate:
            if client_name.find(vm_name) != -1:
                bitrate = str(vm_config.vm_bitrate[vm_name])
        if bitrate == "":
            bitrate = "800000000"
        flow_number = "1"
        for vm_name in vm_config.vm_flow_share:
            if client_name.find(vm_name) != -1:
                flow_number = str(math.ceil(exp.flows * vm_config.vm_flow_share[vm_name]))
        if int(flow_number) == 0:
            flow_number = "1"
        result = vm_c.run(' '.join(
            textwrap.dedent('''
                parallel
                --no-notice
                --xapply
                --files
                --results iperf3
                --max-procs {flows}
            
                /usr/local/bin/iperf3
                --client {server_ip}
                --port {{1}}
                --cport {{2}}
                --bind {client_ip}
                -n {transfer_str}
                --parallel {{3}}
                -b {bitrate}
                -l 1000
                --json
                -E /home/fdmp/distrFile{{4}}.txt
                
                
                ::: {server_ports}
                ::: {client_ports}
                ::: {client_flows}
                ::: {ids}
            ''').splitlines()
            ).format(
                #job_number=len(kwargs['client_ports']),
                #job_number=len(kwargs['server_ports']),
                #job_number=128,
                flows=flow_number,
                server_ip=params['server_ip'],
                server_ports=' '.join(map(str, params['server_ports'])),
                client_ip=params['client_ip'],
                client_ports=' '.join(map(str, params['client_ports'])),
                transfer_str=transfer_str,
                client_flows=' '.join(map(str, params['client_flows'])),
                bitrate=bitrate,
		ids = ' '.join(map(str, params['id'])),
                #exp_length=test_case['time_amount'],
            )
        )
        #print("after parrallel {1} {2}".format(kwargs['server_ip'], kwargs['client_ip']))
        if result.failed:
            raise RuntimeError(result.stderr)
        return result



def stop_process_pool(executor):
    for pid, process in executor._processes.items():
        process.terminate()
    executor.shutdown()


MAX_PAIRS = 3

#DEBUG
def print_loader_pairs(loader_pairs):
    for lp in loader_pairs:
            print(lp)
            print("")

#TODO make using VM database
def get_remote_server_name(pair_number):
    base_str = 'fdmp_at_w4loader{}-clone'
    return base_str.format((pair_number // 2) % MAX_PAIRS + 1)
    

def get_remote_client_name(pair_number):
    base_str = 'fdmp_at_w1loader{}-clone'
    return base_str.format((pair_number // 2) % MAX_PAIRS + 1)


def unite_loaders(loader_pairs):
    unique_pairs = {}
    for lp in loader_pairs:
        if lp['server_ip'] not in unique_pairs:
            unique_pairs[lp['server_ip']] = lp
            unique_pairs[lp['server_ip']]['server_ports'] = [lp['server_ports'],]
            unique_pairs[lp['server_ip']]['client_ports'] = [lp['client_ports'],]
            unique_pairs[lp['server_ip']]['client_flows'] = [lp['client_flows'],]
            unique_pairs[lp['server_ip']]['id'] = [lp['id'],]
            unique_pairs[lp['server_ip']]['distrSeed'] = [lp['distrSeed'],]
        else:
            unique_pairs[lp['server_ip']]['server_ports'].append(lp['server_ports'])
            unique_pairs[lp['server_ip']]['client_ports'].append(lp['client_ports'])
            unique_pairs[lp['server_ip']]['client_flows'].append(lp['client_flows'])
            unique_pairs[lp['server_ip']]['id'].append(lp['id'])
            unique_pairs[lp['server_ip']]['distrSeed'].append(lp['distrSeed'])

    return list(unique_pairs.values())

 

class Runner:
    def __init__(self, test):
        self.tester = test
        self.current_stage = 0

   
    def generate_loader_pairs(self, nflows):
        # assume nflows to divide by 128
        print('-------------------------------')
        print('nflows = {}'.format(nflows))
        loaders = []

        #TODO: check
        self.server_ports_offset = 7000
        self.client_ports_offset = 11001
        self.server_ports_offset_list = []
        self.client_ports_offset_list = []
        i = 0
        seedBase = 15000
        while nflows > 0:
                 self.server_ports_offset_list.append((self.server_ports_offset % 65535) + 10*i) #TODO check i and offset list purpose
                 self.client_ports_offset_list.append((self.client_ports_offset % 65535) + 1000*i)

                 pair1 = {
                     'server_ports': 7000 + 10 * (i // (2 * MAX_PAIRS)),
                     'client_ports': 11001 + 1000 * (i // (2 * MAX_PAIRS)),
                     'client_flows': min(128, nflows),
                     'exp_length': 60,
                     'id': i
                 }
                 nflows -= min(128, nflows)

                 pair2 = dict(**pair1)

                 #TODO make with vm
                 pair1['remote_server_name'] = get_remote_server_name(i)
                 pair1['remote_client_name'] = get_remote_client_name(i)
                 pair1['server_ip'] = pair2['client_ip'] = '10.{}.1.2'.format((i // 2) % MAX_PAIRS + 1)
                 pair2['server_ip'] = pair1['client_ip'] = '10.{}.1.1'.format((i // 2) % MAX_PAIRS + 1)
                 pair1['distrSeed'] = seedBase + i
                 pair2['distrSeed'] = seedBase + i + 1
                 loaders.append(pair1)

                 if nflows > 0:
                    pair2['remote_client_name'] = pair1['remote_server_name']
                    pair2['remote_server_name'] = pair1['remote_client_name']
                    pair2['client_flows'] = min(128, nflows)
                    pair2['id'] = i + 1
                    loaders.append(pair2)
                    nflows -= min(128, nflows)
                 i += 2
        print_loader_pairs(loaders)
        return loaders

 #   def generate_loader_pairs(self, nflows):
 #        # assume nflows to divide by 128
 #        from app.models import VM
 #        loader_pairs = len(VM.query.all()) // 2
 #        npairs = (((nflows + 127) // 128) + 1) // (2 * loader_pairs)
 #        if (npairs == 0): npairs += 1
 #        print(loader_pairs)
 #        loaders = []

 #        #TODO: check
 #        self.server_ports_offset = 7000
 #        self.client_ports_offset = 11001
 #        self.server_ports_offset_list = []
 #        self.client_ports_offset_list = []
 #        s = 0
 #        seedBase = 15000
 #        for i in range(loader_pairs):
 #                print(":::::::::::NPAIRS:::::::")
 #                print(npairs)
 #                self.server_ports_offset_list.append([(self.server_ports_offset % 65535) + 10*x for x in range(npairs)])
 #                self.client_ports_offset_list.append([(self.client_ports_offset % 65535) + 1000*x for x in range(npairs)])
 #                print(self.server_ports_offset_list)
 #                print(self.client_ports_offset_list)
 #                #pair1 = {
 #                #    'server_ports': server_ports_offset_list[i],
 #                #    'client_ports': client_ports_offset_list[i],
 #                #    'client_flows': 64, #flows
 #                #    'exp_length': 60,
 #                #}
 #                pair1 = {
 #                    'server_ports': [7000 + 10*x for x in range(npairs)],
 #                    'client_ports': [11001 + 1000*x for x in range(npairs)],
 #                    #'client_ports': [11001 + 10*x for x in range(1, 128)],
 #                    'client_flows': 128,
 #                    'exp_length': 60,
 #                }
 #                pair2 = dict(**pair1)
 #                #TODO make with vm
 #                pair1['remote_server_name'] = pair2['remote_client_name'] = 'fdmp_at_w4loader{}-clone'.format(i + 1) ## redacted -clone
 #                pair2['remote_server_name'] = pair1['remote_client_name'] = 'fdmp_at_w1loader{}-clone'.format(i + 1) ##redacted
 #                pair1['server_ip'] = pair2['client_ip'] = '10.{}.1.2'.format(i + 1)
 #                pair2['server_ip'] = pair1['client_ip'] = '10.{}.1.1'.format(i + 1)
 #                pair1['distrSeed'] = seedBase + s
 #                pair2['distrSeed'] = seedBase + s + 1
 #                loaders.append(pair1)
 #                loaders.append(pair2)
 #                s += 2
 #        return loaders

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

    def cleanup_testbed(self, exp):
        from app.models import Server

        head = Server.query.filter_by(servername = 'head').all()[0]
        user_head = head.username
        #TODO: we don't need in cleanup, if the topology is same
        try:
            c_server = fabric.connection.Connection(host = 'head', config = conn_config)
            #TODO setup sudo password?
            c_server.run('sudo bash -c "cd /home/{}/netbuilder; ./delete.sh"'.format(user_head))
        except BaseException as e:
            print("Failed to clean up testbed!")
            print(e)
            raise

    def deploy_testbed(self, exp):
        #TODO; check experiment parameters (no rules for subnum 1)
        try:
            start_topology(exp)
            set_qos(exp)
            self.loader_pairs = self.generate_loader_pairs(exp.flows)
            setup_multiloader(self.loader_pairs, exp)
            start_controller(exp)
            start_watch(exp)
        except BaseException as e:
            print("Failed to deploy testbed!")
            print(e)
            raise

    #TODO: move waiting from restart_vms
    def wait_vm(self, exp):
        pass

    def setup_vms(self, exp):
        from app.models import VM
        try:
            vms = VM.query.all()
            n_processes = len(vms)
            param_list = []
            if exp.mode == 'mixed':
                for num in range(n_processes):
                    p = dict(params)
                    if (num // 2) % 2:
                        p['mode'] = 'single'
                        p['subflow_per_session'] = 1
                        p['cc_algorithm'] = 'cubic'
                    else:
                        p['mode'] = 'mp'
                    param_list.append(p)
            #TODO mixed mode
                    
            for vm in vms:
                setup_loader(exp, vm)

            setLoaderQos(exp.subflow, exp.protocol)
        except BaseException as e:
            print('Failed to setup vms!')
            print(e)

    def clean_iperf3_results(self, exp):
        from app.models import VM
        vms = VM.query.all()
        for vm in vms:
            vm_c = fabric.connection.Connection(host = vm.vmname, config = conn_config)
            vm_c.run('rm -rf iperf3 || true')
            vm_c.run('pkill -HUP parallel || true')
        
    def start_collectd(self, exp):
        import io
        import textwrap
        head_c = fabric.connection.Connection(host = 'head', config = conn_config)
        if head_c.run('[ -f ~/collectd.pid ] && pkill -HUP --pidfile ~/collectd.pid || true').failed:
            raise RuntimeError('Failed to stop collectd launched before!')
        if head_c.run('rm -rf /home/fdmp/csv || true').failed:
            raise RuntimeError('Failed to clean up csv folder!')
        head_c.put(io.StringIO(
                    textwrap.dedent("""
                        interval 1
                        LoadPlugin csv
                        LoadPlugin interface
                        LoadPlugin logfile
                        <Plugin interface>
                            Interface "/^veth*/"
                        </Plugin>
                        <Plugin logfile>
                            LogLevel info
                            File "/home/fdmp/collectd.log"
                            Timestamp true
                        </Plugin>
                        <Plugin csv>
                            DataDir "/home/fdmp/csv"
                        </Plugin>
                    """)),
                    'collectd.conf'
                )
        if head_c.run('timeout -s9 100 collectd -C ~/collectd.conf -P ~/collectd.pid').failed:
            raise RuntimeError('Failed to run collectd')

    def run_iperf3_loaders(self, exp):
        import time
        import threading 

        loader_pairs = unite_loaders(self.loader_pairs)
        threads = []
        for p in loader_pairs:
            thr = threading.Thread(target = start_iperf3_servers, args = (p,))
            thr.start()
            threads.append(thr)
        time.sleep(5)
        for p in loader_pairs:
            thr = threading.Thread(target = start_iperf3_clients, args = (p, exp))
            thr.start()
            threads.append(thr)
            print("client has started")

        for thr in threads:
            thr.join(timeout = exp.time)
        print("All threads have been finished")

    def collect_results(self, exp):
        from pathlib import Path
        try:
                results_directory = 'results/' + exp.sha_hash()
                Path(results_directory).mkdir(parents=True, exist_ok=True)
                loader_pairs = unite_loaders(self.loader_pairs)
                kill_controller(exp)
                kill_watch(exp)
                collect_collectd_results(results_directory)
                collect_controller_results(results_directory)
                collect_watch_results(results_directory)
                collect_iperf3_results(results_directory, loader_pairs)
        except BaseException as e:
            print("Failed to collect results!")
            print(e)
            raise



    stages = [
        restart_vms,
        cleanup_testbed,
        deploy_testbed,
        wait_vm,
        setup_vms,
        clean_iperf3_results,
        start_collectd,
        run_iperf3_loaders,
        collect_results,
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
                # for DEBUG
                #break
                self.current_experiment = self.queue.pop(0)
                self.current_stage = STAGES[0]
                exp_thread = threading.Thread(target = self.runner.run, args = (self.current_experiment, ))
                #exp_thread = multiprocessing.Process(target = self.runner.run, args = (self.current_experiment, ))
                exp_thread.start() 
                exp_thread.join(timeout = RUN_TIMEOUT)
                #TODO: process hanging experiments
                if exp_thread.is_alive():
                    print("EXIT of EXPERIMENT due to TIMEOUT")
                    #exp_thread.terminate()
                print("Len of queue: {}".format(len(self.queue)))

                from app import db
                self.current_experiment.completed = True
                local_object = db.session.merge(self.current_experiment)
                db.session.add(local_object)
                db.session.commit()
                # for DEBUG
                #break

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


