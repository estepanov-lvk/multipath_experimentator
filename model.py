#! /usr/bin/python3

import math
import numpy
import pickle

#ALL_TOPOS = ['Garr201101', 'Belnet2007', 'Deltacom', 'TLex', 'Dataxchange', 'Belnet2003', 'Garr201108', 'GtsSlovakia', 'Uninett2010', 'Bellcanada', 'Missouri', 'HiberniaUk', 'Geant2010', 'Ilan', 'Garr201107', 'Palmetto', 'HurricaneElectric', 'RedBestel', 'Nordu1989', 'Nordu2005', 'GtsRomania', 'Funet', 'CrlNetworkServices', 'Marnet', 'Oxford', 'Columbus', 'VtlWavenet2008', 'Belnet2009', 'Renam', 'Aconet', 'HostwayInternational', 'Abvt', 'Garr201105', 'Napnet', 'Getnet', 'Garr199901', 'Sanren', 'Renater2010', 'Evolink', 'Garr200912', 'KentmanJul2005', 'HiberniaUs', 'Heanet', 'DialtelecomCz', 'Ion', 'Claranet', 'Dfn', 'Singaren', 'RusTTK', 'Ulaknet', 'Eenet', 'Harnet', 'Garr201110', 'BsonetEurope', 'BtAsiaPac', 'BtEurope', 'GtsHungary', 'HiberniaNireland', 'Surfnet', 'Arn', 'LambdaNet', 'Garr201102', 'Renater2004', 'Tinet', 'Cernet', 'Zamren', 'Cesnet1993', 'Renater2001', 'Reuna', 'Belnet2008', 'Amres', 'Itnet', 'Mren', 'Garr201201', 'UniC', 'Renater2008', 'Ntelos', 'Peer1', 'AttMpls', 'Garr201003', 'NetworkUsa', 'Cesnet200511', 'Sinet', 'Cesnet2001', 'Arnes', 'Bandcon', 'Pern', 'KentmanFeb2008', 'Chinanet', 'Nextgen', 'Grnet', 'HiberniaIreland', 'Garr201001', 'Marwan', 'Arpanet196912', 'Belnet2004', 'Belnet2010', 'Garr201111', 'Sago', 'Quest', 'Tw', 'Ibm', 'Sanet', 'Garr200909', 'Aarnet', 'Rediris', 'Garr201104', 'Internetmci', 'Garr201112', 'Cwix', 'Garr199905', 'EliBackbone', 'GtsCe', 'Globalcenter', 'Garr200109', 'Ntt', 'Intranetwork', 'UsSignal', 'Litnet', 'Grena', 'Shentel', 'KentmanAug2005', 'PionierL1', 'Xeex', 'Layer42', 'Spiralight', 'Epoch', 'Carnet', 'Xspedius', 'Rhnet', 'Rnp', 'Karen', 'Internode', 'Garr200902', 'Latnet', 'Colt', 'Airtel', 'Intellifiber', 'AsnetAm', 'Agis', 'Myren', 'Goodnet', 'Janetbackbone', 'HiberniaGlobal', 'Cesnet201006', 'Packetexchange', 'Cesnet200603', 'Ai3', 'PionierL3', 'Garr200112', 'Geant2009', 'Garr201012', 'Biznet', 'Savvis', 'WideJpn', 'Niif', 'Cudi', 'Garr201007', 'Vinaren', 'Pacificwave', 'Telcove', 'Gambia', 'Garr199904', 'Belnet2005', 'Renater2006', 'Gridnet', 'Garr200404', 'Restena', 'Iij', 'Navigata', 'Fatman', 'VtlWavenet2011', 'Gblnet', 'UsCarrier', 'Uunet', 'Iris', 'Nsfnet', 'GtsCzechRepublic', 'Ans', 'Geant2001', 'GtsPoland', 'Roedunet', 'BtLatinAmerica', 'Netrail', 'Uran', 'Sprint', 'VisionNet', 'Istar', 'BeyondTheNetwork', 'TataNld', 'Azrena', 'Fccn', 'SwitchL3', 'Nordu1997', 'Garr201010', 'Highwinds', 'Cynet', 'HiberniaCanada', 'Esnet', 'Jgn2Plus', 'Garr201103', 'Cesnet200304', 'Nsfcnet', 'Janetlense', 'Kreonet', 'Atmnet', 'Arpanet19719', 'Garr200212', 'Bren', 'RoedunetFibre', 'Garr201004', 'Basnet', 'Bics', 'Darkstrand', 'Integra', 'Cogentco', 'Padi', 'Canerie', 'Uninet', 'BtNorthAmerica', 'Sunet', 'Abilene', 'KentmanJan2011', 'Ernet', 'Belnet2006', 'IowaStatewideFiberMap', 'Renater1999', 'Bellsouth', 'Digex', 'Easynet', 'Arpanet19728', 'Iinet', 'Uninett2011', 'Arpanet19706', 'Switch', 'Compuserve', 'Psinet', 'Forthnet', 'Garr200908', 'Eunetworks', 'York', 'Cesnet1997', 'Cesnet1999', 'Garr201109', 'Twaren', 'Garr201005', 'Arpanet19723', 'Telecomserbia', 'Noel', 'Cesnet200706', 'Geant2012', 'KentmanApr2007', 'Garr201008', 'Globenet', 'Syringa', 'Bbnplanet']
ALL_TOPOS = ['Garr201101'] #'Belnet2007', 'Deltacom', 'TLex', 'Dataxchange', 'Belnet2003', 'Garr201108', 'GtsSlovakia', 'Uninett2010', 'Bellcanada', 'Missouri', 'HiberniaUk', 'Geant2010', 'Ilan', 'Garr201107', 'Palmetto', 'HurricaneElectric', 'RedBestel', 'Nordu1989', 'Nordu2005', 'GtsRomania', 'Funet', 'CrlNetworkServices', 'Marnet', 'Oxford', 'Columbus', 'VtlWavenet2008', 'Belnet2009', 'Renam', 'Aconet', 'HostwayInternational', 'Abvt', 'Garr201105', 'Napnet', 'Getnet', 'Garr199901', 'Sanren', 'Renater2010', 'Evolink', 'Garr200912', 'KentmanJul2005', 'HiberniaUs', 'Heanet', 'DialtelecomCz', 'Ion', 'Claranet', 'Dfn', 'Singaren', 'RusTTK', 'Ulaknet', 'Eenet', 'Harnet', 'Garr201110', 'BsonetEurope', 'BtAsiaPac', 'BtEurope', 'GtsHungary', 'HiberniaNireland', 'Surfnet', 'Arn', 'LambdaNet', 'Garr201102', 'Renater2004', 'Tinet', 'Cernet', 'Zamren', 'Cesnet1993', 'Renater2001', 'Reuna', 'Belnet2008', 'Amres', 'Itnet', 'Mren', 'Garr201201', 'UniC', 'Renater2008', 'Ntelos', 'Peer1', 'AttMpls', 'Garr201003', 'NetworkUsa', 'Cesnet200511', 'Sinet', 'Cesnet2001', 'Arnes', 'Bandcon', 'Pern', 'KentmanFeb2008', 'Chinanet', 'Nextgen', 'Grnet', 'HiberniaIreland', 'Garr201001', 'Marwan', 'Arpanet196912', 'Belnet2004', 'Belnet2010', 'Garr201111', 'Sago', 'Quest', 'Tw', 'Ibm', 'Sanet', 'Garr200909', 'Aarnet', 'Rediris', 'Garr201104', 'Internetmci', 'Garr201112', 'Cwix', 'Garr199905', 'EliBackbone', 'GtsCe', 'Globalcenter', 'Garr200109', 'Ntt', 'Intranetwork', 'UsSignal', 'Litnet', 'Grena', 'Shentel', 'KentmanAug2005', 'PionierL1', 'Xeex', 'Layer42', 'Spiralight', 'Epoch', 'Carnet', 'Xspedius', 'Rhnet', 'Rnp', 'Karen', 'Internode', 'Garr200902', 'Latnet', 'Colt', 'Airtel', 'Intellifiber', 'AsnetAm', 'Agis', 'Myren', 'Goodnet', 'Janetbackbone', 'HiberniaGlobal', 'Cesnet201006', 'Packetexchange', 'Cesnet200603', 'Ai3', 'PionierL3', 'Garr200112', 'Geant2009', 'Garr201012', 'Biznet', 'Savvis', 'WideJpn', 'Niif', 'Cudi', 'Garr201007', 'Vinaren', 'Pacificwave', 'Telcove', 'Gambia', 'Garr199904', 'Belnet2005', 'Renater2006', 'Gridnet', 'Garr200404', 'Restena', 'Iij', 'Navigata', 'Fatman', 'VtlWavenet2011', 'Gblnet', 'UsCarrier', 'Uunet', 'Iris', 'Nsfnet', 'GtsCzechRepublic', 'Ans', 'Geant2001', 'GtsPoland', 'Roedunet', 'BtLatinAmerica', 'Netrail', 'Uran', 'Sprint', 'VisionNet', 'Istar', 'BeyondTheNetwork', 'TataNld', 'Azrena', 'Fccn', 'SwitchL3', 'Nordu1997', 'Garr201010', 'Highwinds', 'Cynet', 'HiberniaCanada', 'Esnet', 'Jgn2Plus', 'Garr201103', 'Cesnet200304', 'Nsfcnet', 'Janetlense', 'Kreonet', 'Atmnet', 'Arpanet19719', 'Garr200212', 'Bren', 'RoedunetFibre', 'Garr201004', 'Basnet', 'Bics', 'Darkstrand', 'Integra', 'Cogentco', 'Padi', 'Canerie', 'Uninet', 'BtNorthAmerica', 'Sunet', 'Abilene', 'KentmanJan2011', 'Ernet', 'Belnet2006', 'IowaStatewideFiberMap', 'Renater1999', 'Bellsouth', 'Digex', 'Easynet', 'Arpanet19728', 'Iinet', 'Uninett2011', 'Arpanet19706', 'Switch', 'Compuserve', 'Psinet', 'Forthnet', 'Garr200908', 'Eunetworks', 'York', 'Cesnet1997', 'Cesnet1999', 'Garr201109', 'Twaren', 'Garr201005', 'Arpanet19723', 'Telecomserbia', 'Noel', 'Cesnet200706', 'Geant2012', 'KentmanApr2007', 'Garr201008', 'Globenet', 'Syringa', 'Bbnplanet']
STAGES = ['loader_pairs', 'schedule_flows', 'controller', 'finish']
MAX_PAIRS = 3


RUN_TIMEOUT = 2000
RESTART_VMS_TIMEOUT = 50

#TODO move IFMAP to models
IF_MAP = { #interfaces on head to loaders 
    'fdmp_at_w1loader1-clone': 'enp13s0f0', 
    'fdmp_at_w1loader2-clone': 'enp13s0f1',
    'fdmp_at_w1loader3-clone': 'enp15s0f1',
    #'fdmp_at_w1loader4': 'enp15s0f1',
    'fdmp_at_w4loader1-clone': 'enp8s0f0',
    'fdmp_at_w4loader2-clone': 'enp131s0f0',
    'fdmp_at_w4loader3-clone': 'enp131s0f1',
    #'fdmp_at_w4loader4': 'enp15s0f0',
}
BORDER_SWITCH = 1234

USER_MAP = {
    "head": 'arccn',
    "w1": 'arccn',
    "w4": 'fdmp',
    "w1loader1-clone": 'fdmp',
    "w1loader2-clone": 'fdmp',
    "w1loader3-clone": 'fdmp',
    #"w1loader4": 'fdmp',
    "w4loader1-clone": 'fdmp',
    "w4loader2-clone": 'fdmp',
    "w4loader3-clone": 'fdmp',
    #"w4loader4": 'fdmp',
}


# head - where topology is
# w1, w2, ..., w4 - where loaders are
# loader1, ... - VM for load
class VMConfig(object):
    def __init__(self):
        self.hosts = {
            'head': '172.30.2.1',

            'w1': '172.30.2.11',
            'w4': '172.30.2.14',

            'w1loader1-clone': '172.30.2.111',
            'w1loader2-clone': '172.30.2.112',
            'w1loader3-clone': '172.30.2.113',
            #'w1loader4': '172.30.2.114',
            'w4loader1-clone': '172.30.2.141',
            'w4loader2-clone': '172.30.2.142',
            'w4loader3-clone': '172.30.2.143',
            #'w4loader4': '172.30.2.144',
        }
        self.vm_allocation = {
            'w1loader1-clone': ['w1', 'w1loader1-clone'], #or is it username?
            'w1loader2-clone': ['w1', 'w1loader2-clone'],
            'w1loader3-clone': ['w1', 'w1loader3-clone'],
            #'w1loader4': ['w1', 'w1loader4'],
            'w4loader1-clone': ['w4', 'w4loader1-clone'],
            'w4loader2-clone': ['w4', 'w4loader2-clone'],
            'w4loader3-clone': ['w4', 'w4loader3-clone'],
            #'w4loader4': ['w4', 'w4loader4'],
            
            
        }
        self.vm_data_if = {
            'w1loader1-clone': ['ens9', '10.1.1.1'],
            'w4loader1-clone': ['ens9', '10.1.1.2'],
            'w1loader2-clone': ['ens9', '10.2.1.1'],
            'w4loader2-clone': ['ens9', '10.2.1.2'],
            'w1loader3-clone': ['ens9', '10.3.1.1'],
            'w4loader3-clone': ['ens9', '10.3.1.2'],
            #'w1loader4': ['ens9', '10.4.1.1'],
            #'w4loader4': ['ens9', '10.4.1.2'],
            
            
        }
        self.vm_qos_classes = {
            133 : ['w1loader1-clone'], #kbps
            1200 : ['w4loader1-clone'],
            500 : ['w1loader2-clone'],
            2750 : ['w4loader2-clone'],
            800 : ['w1loader3-clone'],
            5000 : ['w4loader3-clone'],
        }
        self.vm_flow_share = {
            'w1loader1-clone' : 0.01, # <144p
            'w1loader2-clone' : 0.1, # 144-240p
            'w1loader3-clone' : 0.1, # 240-360p
            'w4loader1-clone' : 0.2, # 360-480p
            'w4loader2-clone' : 0.4, # 480-720p
            'w4loader3-clone' : 0.2  # >720p
        }
        self.vm_transfer_size = {
            415625 : ['w1loader1-clone'],
            15625000 : ['w1loader2-clone'],
            25000000 : ['w1loader3-clone'],
            37500000 : ['w4loader1-clone'],
            85937500 : ['w4loader2-clone'],
            156250000 : ['w4loader3-clone'],
            #100000000 : ['w1loader1-clone', 'w4loader1-clone'],
            #100000000 : ['w1loader2-clone', 'w4loader2-clone'],
            #100000000 : ['w1loader3-clone', 'w4loader3-clone'],
        }
        self.vm_bitrate = {
            'w1loader1-clone': 133000, 
            'w1loader2-clone': 500000,
            'w1loader3-clone': 800000,
            'w4loader1-clone': 1200000,
            'w4loader2-clone': 2750000, #bits/sec
            'w4loader3-clone': 5000000,
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
    difference = max(s) + 0.1
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


class ExperimentAddForm():
    mode = ['mp']
    model = ['mcmf']
    subflow = ['2', '3']
    cc = ['cubic']
    distribution = ['weibull']
    #protocol = ['mptcp', 'fdmp']
    topos = ALL_TOPOS
    time = [180]
    flows = [10000, 64000]
    poles = ['70']
    probe = '1'
    poles_seed = ['0']
    routes_seed = ['0']


class Experiment():
    gid = 1

    def __repr__(self):
        return '<Experiment {}>'.format(self.id)

    def __init__(self, mode, model, subflow, cc, distribution, topo, poles, flows, poles_seed, routes_seed, time, probe, completed):
        self.id = Experiment.gid
        Experiment.gid += 1
        self.mode = mode
        self.model = model
        self.subflow = subflow
        self.cc = cc
        self.distribution = distribution
        self.topo = topo
        self.poles = poles
        self.flows = flows
        self.poles_seed = poles_seed
        self.routes_seed = routes_seed
        #self.protocol = protocol
        self.time = time
        self.probe = probe
        self.completed = completed

    def __repr__(self):
        unique_str = ''
        unique_str += str(self.mode) + '_'
        unique_str += str(self.model)+ '_'
        unique_str += str(self.subflow)+ '_'
        unique_str += str(self.topo)+ '_'
        unique_str += str(self.poles)+ '_'
        unique_str += str(self.flows)+ '_'
        unique_str += str(self.poles_seed)+ '_'
        unique_str += str(self.routes_seed)+ '_'
        unique_str += str(self.cc)+ '_'
        #unique_str += str(self.protocol)
        unique_str += str(self.distribution)+ '_'
        unique_str += str(self.time)+ '_'
        unique_str += str(self.probe)+ '_'
        return unique_str

    def sha_hash(self):
        import hashlib

        unique_str = ''
        unique_str += str(self.mode)
        unique_str += str(self.model)
        unique_str += str(self.subflow)
        unique_str += str(self.topo)
        unique_str += str(self.poles)
        unique_str += str(self.flows)
        unique_str += str(self.poles_seed)
        unique_str += str(self.routes_seed)
        unique_str += str(self.cc)
        #unique_str += str(self.protocol)
        unique_str += str(self.distribution)
        unique_str += str(self.time)
        unique_str += str(self.probe)
        return hashlib.sha1(unique_str.encode()).hexdigest()



def make_list(s):
    #a = eval(s)
    a = s
    if (type(a) != type(list()) and type(a) != type(tuple())):
        a = [a]
    return a


def generate_experiments(form):
    import itertools

    new_experiments = []

    for x in itertools.product(
            form.mode,
            form.model,
            make_list(form.subflow),
            form.cc,
            form.distribution,
            form.topos,
            make_list(form.poles),
            make_list(form.flows),
            make_list(form.poles_seed),
            make_list(form.routes_seed),
            #form.protocol,
            make_list(form.time)
            ):
        #checks?
        
        #find the number of similar experiments
        max_probe = 0
        for i in range(int(form.probe)):
            experiment = Experiment(
                    mode = x[0],
                    model = x[1],
                    subflow = x[2],
                    cc = x[3],
                    distribution = x[4],
                    topo = x[5],
                    poles = x[6],
                    flows = x[7],
                    poles_seed = x[8],
                    routes_seed = x[9],
                    #protocol = x[10],
                    #time = x[11],
                    time = x[10],
                    probe = max_probe + i,
                    completed = False)
            new_experiments.append(experiment)

    return new_experiments

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
    def __init__(self):
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
        #print_loader_pairs(loaders)
        return loaders

    def update_stage(self):
        self.current_stage += 1
        print(STAGES[self.current_stage])

    def deploy_testbed(self, exp):
        #TODO; check experiment parameters (no rules for subnum 1)
        try:
            #start_topology(exp)
            #set_qos(exp)
            print("DEPLOY")
            self.loader_pairs = self.generate_loader_pairs(exp.flows)
            #setup_multiloader(self.loader_pairs, exp)
            #start_controller(exp)
            #start_watch(exp)
        except BaseException as e:
            print("Failed to deploy testbed!")
            print(e)
            raise

    def schedule_flows(self, exp):
        print("SCHEDULE FLOWS")
        #loader_pairs = unite_loaders(self.loader_pairs)
        self.flows = []
        for params in self.loader_pairs:
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
                flow_number = params['client_flows']

                #print(params['distrSeed'])
                flow_start_time = getDistr(exp.distribution, exp.time, params['client_flows'], params['distrSeed'])
                for i in range(int(flow_number)):
                    new_flow = Flow(params['client_ip'], params['server_ip'], params['client_ports'] + i, params['server_ports'])
                    new_flow.start_time = flow_start_time[i]
                    new_flow.transfer = transfer_str
                    new_flow.bitrate = bitrate
                    self.flows.append(new_flow)
                    #print(new_flow)
                    events.append(Event(new_flow.start_time, new_flow, "add"))
                    # bytes * 8 / bits/s
                    #print(int(new_flow.transfer))
                    #print(int(new_flow.bitrate))
                    #print("")
                    events.append(Event(new_flow.start_time + int(new_flow.transfer) * 8 / int(new_flow.bitrate), new_flow, "delete"))


    def create_controller_config(self, topo, subflow, poles, proto):
        BANDWIDTH = 1000000 #Kbit/s  current value is 1 Gbit/s
        print(topo, subflow, poles)
        dict1 = {}
        dict1["sub_num"] = subflow
        dict1["seed"] = 1
        dict1["pole_ratio"] = poles
        dict1["protocol"] = proto
        dict_topo = {}
        dict_topo["name"] = topo
        dict_edges = {}
        list_edges = []
        with open("./app/experiment/topo/" + topo, 'rb') as fp:
            graph = pickle.load(fp)
        
        edges = graph.edges()
        edges_filtered = []
        dict1['edges'] = {}
        for t in edges:
            if not t in edges_filtered:
                edges_filtered.append(t)
        for t in edges_filtered:
            dict_edge = {}
            dict_edge["s_node"] = t[0]
            dict_edge["d_node"] = t[1]
            dict_edge["bw"] = BANDWIDTH
            dict_edge["remain_bw"] = BANDWIDTH
            list_edges.append(dict_edge)

            if t[0] not in dict1['edges']:
                dict1['edges'][t[0]] = {}
            dict1['edges'][t[0]][t[1]] = {
                'bw': BANDWIDTH,
                'remain_bw': BANDWIDTH
            }


            dict_edge = {}
            dict_edge["s_node"] = t[1]
            dict_edge["d_node"] = t[0]
            dict_edge["bw"] = BANDWIDTH
            dict_edge["remain_bw"] = BANDWIDTH
            list_edges.append(dict_edge)

            if t[1] not in dict1['edges']:
                dict1['edges'][t[1]] = {}
            dict1['edges'][t[1]][t[0]] = {
                'bw': BANDWIDTH,
                'remain_bw': BANDWIDTH
            }
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
        return dict1


    def init_routes(self, topo, subflow):
        import json
        all_routes = json.load(open("routes/"+topo+".json"))
        return all_routes[str(subflow)]

    def init_poles(self, config):
        import random
        random.seed(int(config['seed']))
        config['poles'] = []
        nodes = len(config['topo']['nodes'])
        if int(config['pole_ratio']) == 100:
            config['poles'] = config['topo']['nodes']
        else:
                while len(config['poles']) < max(nodes * int(config['pole_ratio']) / 100, 2):
                    new_pole_index = random.randint(0, nodes-1)
                    if config['topo']['nodes'][new_pole_index] in config['poles']:
                        continue
                    config['poles'].append(config['topo']['nodes'][new_pole_index])
        config['poles'].sort()

    def route_intersection(self, route_id, route_pos, flow, completed_subflows, routes):
        intersections = []
        first = routes[str(flow.s_node)][str(flow.d_node)][route_id][route_pos]
        second = routes[str(flow.s_node)][str(flow.d_node)][route_id][route_pos + 1]

        for i in range(flow.sub_num):
            if i in completed_subflows:
                continue

            route = routes[str(flow.s_node)][str(flow.d_node)][i]
            for j in range(len(route) - 1):
                if route[j] == first and route[j+1] == second:
                    intersections.append(i)
                    continue

        return intersections

        

    def find_bottleneck(self, flow, completed_subflows, routes, config):
        bn = {}
        bn['rate'] = 9999999999999 #BIG VALUE
        #print(routes[str(flow.s_node)][str(flow.d_node)])
        
        for i in range(flow.sub_num):
            if i in completed_subflows:
                continue

            route = routes[str(flow.s_node)][str(flow.d_node)][i]
            for j in range(len(route) - 1):
                intersections = self.route_intersection(i, j, flow, completed_subflows, routes)
                new_rate = config['edges'][route[j]][route[j+1]]['remain_bw'] / len(intersections)
                if new_rate < bn['rate']:
                    bn['src'] = route[j]
                    bn['dst'] = route[j+1]
                    bn['routes'] = intersections
                    bn['rate'] = min(new_rate, (int(flow.bitrate) / 1000 - flow.rate) / (flow.sub_num - len(completed_subflows)))
        return bn
        

    def reduce_bw_on_route(self, config, flow, routes, route_id, bw):
        route = routes[str(flow.s_node)][str(flow.d_node)][route_id]
        for i in range(len(route) - 1):
            config['edges'][route[i]][route[i+1]]['remain_bw'] -= bw

    def add_bw_on_route(self, config, flow, routes, route_id, bw):
        route = routes[str(flow.s_node)][str(flow.d_node)][route_id]
        for i in range(len(route) - 1):
            config['edges'][route[i]][route[i+1]]['remain_bw'] += bw

    def remove_flow(self, config, flow, routes):
        for i in range(len(flow.route_ids)):
            self.add_bw_on_route(config, flow, routes, flow.route_ids[i], flow.rates[i])

    def add_route_length(self, config, flow, routes):
        flow.route_lengths = []
        for i in range(len(flow.route_ids)):
            route = routes[str(flow.s_node)][str(flow.d_node)][flow.route_ids[i]]
            flow.route_lengths.append(len(route) - 1)

    def get_route_bw(self, config, flow, routes, route_id):
        bw = 999999999999999999 #BIG VALUE
        route = routes[str(flow.s_node)][str(flow.d_node)][route_id]
        for i in range(len(route) - 1):
            bw = min(bw, config['edges'][route[i]][route[i+1]]['remain_bw'])
            
        return bw

    def static_routes(self, config, flow, routes):
        flow.sub_num = int(config['sub_num'])
        flow.rate = 0
        flow.rates = [0] * int(config['sub_num'])
        flow.route_ids = list(range(flow.sub_num))
        completed_subflows = set()
        while len(completed_subflows) != int(config['sub_num']):
            bn = self.find_bottleneck(flow, completed_subflows, routes, config)

            for i in range(flow.sub_num):
                if i in completed_subflows:
                    continue

                flow.rates[i] += bn['rate']
                flow.rate += bn['rate']
                self.reduce_bw_on_route(config, flow, routes, i, bn['rate'])
            for fl in bn['routes']:
                completed_subflows.add(fl)
            for i in range(flow.sub_num):
                if i in completed_subflows:
                    continue

                if self.get_route_bw(config, flow, routes, i) <= 0:
                    completed_subflows.add(i)

        if (sum(flow.rates) < int(flow.bitrate) / 1000):
            flow.status = False
            for i in range(len(flow.rates)):
                self.add_bw_on_route(config, flow, routes, i, flow.rates[i])
        else:
            flow.status = True
            

        #print(flow.rates)
        #print(flow.s_node, flow.d_node)
        #print(flow.status)

    def get_new_route_by_rate(self, config, flow, routes, completed_subflows):
            new_sub = 0
            new_rate = -1
            for i in range(flow.sub_num):
                if i in completed_subflows:
                    continue

                i_bw = self.get_route_bw(config, flow, routes, i)
                if i_bw > new_rate:
                    new_sub = i
                    new_rate = i_bw
            return (new_rate, new_sub)


    def get_new_route_by_length(self, config, flow, routes, completed_subflows):
            new_sub = 0
            new_rate = -1
            new_length = 9999999999
            for i in range(flow.sub_num):
                if i in completed_subflows:
                    continue

                i_length = len(routes[str(flow.s_node)][str(flow.d_node)][i])
                i_bw = self.get_route_bw(config, flow, routes, i)
                if i_length < new_length:
                    new_sub = i
                    new_rate = i_bw
                    new_length = i_length
            return (new_rate, new_sub)


    def dynamic_routes(self, config, flow, routes):
        flow.sub_num = int(config['sub_num'])
        flow.rate = 0
        flow.rates = []
        flow.route_ids = []
        completed_subflows = set()
        while (flow.rate < int(flow.bitrate) / 1000 and len(completed_subflows) < flow.sub_num):
            new_rate, new_sub = self.get_new_route_by_rate(config, flow, routes, completed_subflows)
            new_rate = min(new_rate, int(flow.bitrate) / 1000 - flow.rate)
            flow.rate += new_rate
            flow.rates.append(new_rate)
            flow.route_ids.append(new_sub)
            self.reduce_bw_on_route(config, flow, routes, new_sub, new_rate)
            completed_subflows.add(new_sub)
        if (flow.rate < int(flow.bitrate) / 1000):
            flow.status = False
            self.remove_flow(config, flow, routes)
        else:
            flow.status = True


    def controller(self, exp):
        exp.results = {}
        for protocol in ['mptcp', 'fdmp']:
                exp.protocol = protocol
                config = self.create_controller_config(exp.topo, exp.subflow, exp.poles, exp.protocol)
                routes = self.init_routes(exp.topo, exp.subflow)
                self.init_poles(config)
                #print(config)
                #print(routes)
                events.sort(key=lambda x: x.time)
                import random
                random.seed(1)
                for event in events:
                    if event.event == "add":
                        event.flow.s_node = random.choice(config["poles"])
                        event.flow.d_node = random.choice(config["poles"])
                        while event.flow.s_node == event.flow.d_node:
                                event.flow.d_node = random.choice(config["poles"])
                        if exp.protocol == 'mptcp':
                                self.static_routes(config, event.flow, routes)
                        elif exp.protocol == 'fdmp':
                                self.dynamic_routes(config, event.flow, routes)

                    if event.event == 'delete':
                        self.remove_flow(config, event.flow, routes)
                exp.results[protocol] = {}
                exp.results[protocol]['config'] = config
                for flow in self.flows:
                    self.add_route_length(config, flow, routes)
                from copy import deepcopy
                exp.results[protocol]['flows'] = deepcopy(self.flows)
                print("Success: ", sum(int(x.status) for x in self.flows), " from ", len(self.flows))
                #self.schedule_flows(exp)
        import pickle
        write_file = open('model_results/'+str(exp), 'wb')
        pickle.dump(exp, write_file)

            #print(event.time)
        #print(config['edges'])
        #for flow in self.flows:
        #    print(flow.rates)


    stages = [
        deploy_testbed,
        schedule_flows,
        controller
        ]


    def run(self, exp):
        self.current_stage = 0
        print(STAGES[self.current_stage])

        for stage in self.stages:
            stage(self, exp)
            self.update_stage()


class Flow():
    def __init__(self, src_ip, dst_ip, src_port, dst_port):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port

    def __repr__(self):
        rep = ''
        rep += self.src_ip + '\n'
        rep += self.dst_ip + '\n'
        rep += str(self.src_port) + '\n'
        rep += str(self.dst_port) + '\n'
        rep += str(self.start_time) + '\n'
        return rep

class Event():
    def __init__(self, time, flow, event):
        self.time = time
        self.flow = flow
        self.event = event

events = []

if __name__ == '__main__':
    runner = Runner()
    exps = generate_experiments(ExperimentAddForm())
    for exp in exps:
        print(exp)
        events = []
        runner.run(exp)
        #print(len(events))
        #break
