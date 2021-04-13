#!/usr/bin/env python3

import collections
import concurrent.futures
import json
import numpy
import pathlib
import re
import tarfile
import networkx as nx
import pickle


def parse_collectd(filename):
    """
    :param filename:
        *.tar.gz with interface metrics as
        collected by write_csv module of collectd
    :returns time_series
        time_series : secs_since_epoch -> interface_snapshot
        interface_snapshot : interface -> metrics
        metrics : namedtuple (packets_tx, packets_rx, octets_tx, octet_rx, errors_tx, errors_rx)
    """
    time_series = dict()
    tar = tarfile.open(str(filename), 'r:gz')
    for member in tar.getmembers():
        if member.isfile():

            interface, attr_group = pathlib.Path(member.name).parts[-2:]
            attr_group = attr_group.split('-', 1)[0].split('_')[1]
            interface = interface.split('-', 1)[1]

            old_tx, old_rx = 0.0, 0.0
            for line in tar.extractfile(member).readlines()[1:-1]:
                epoch, rx, tx = line.decode().split(',')
                snapshot = time_series.setdefault(int(float(epoch)), dict())
                attr_dict = snapshot.setdefault(interface, dict())
                attr_dict['{}_rx'.format(attr_group)] = int(float(rx) - old_rx)
                attr_dict['{}_tx'.format(attr_group)] = int(float(tx) - old_tx)
                old_rx, old_tx = float(rx), float(tx)

    metrics_args = ['packets_tx', 'packets_rx', 'octets_tx', 'octets_rx', 'errors_tx', 'errors_rx']
    metrics = collections.namedtuple('metrics', metrics_args)

    for snapshot in time_series.values():
        for interface, attr_dict in snapshot.items():
            snapshot[interface] = metrics(**attr_dict)

    if not time_series:
        raise RuntimeError('Collected empty series!')
    return time_series


def parse_iperf(foldername):
    """
    :param foldername:
        folder with *.tar.gz files of iperf3 dumps
        as collected from loaders
    :return: time_series
        time_series : secs_since_epoch -> flow snapshot
        flow_snapshot : five_tuple -> metrics
        five_tuple: namedtuple (local_host, local_port, remote_host, remote_port)
        metrics : namedtuple (bytes, retransmits, snd_cwnd, rtt)
    """
    #print("DBG: in parse iperf with {}".format(foldername))
    time_series = dict()
    flow_attr = collections.namedtuple('flow_attr', ['local_host', 'local_port', 'remote_host', 'remote_port'])
    metrics = collections.namedtuple('metrics', ['bytes', 'retransmits', 'snd_cwnd', 'rtt'])

    for filename in pathlib.Path(foldername).glob('*.tar.gz'):
        tar = tarfile.open(str(filename), 'r:gz')
        print("DBG: opened tarfile {}".format(filename))
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith('stdout'):
                print("DBG: parsing stdout, member is {}".format(member))
                extracted = tar.extractfile(member)
                print("DBG: extracted file")
                readFile = extracted.read()
                print("DBG: read file ")
                
                #exit(0)
                content = json.loads(readFile.decode())
                print("DBG: start init")
                start = content['start']
                print("DBG: getting client")
                client = start.get('connecting_to', None)
                print("DBG: got client")
                if client is not None:
                    connections = {
                        x['socket']: flow_attr(**{k: v for k, v in x.items() if k in flow_attr._fields})
                        for x in start['connected']
                    }
                    
                    for x in start['connected']:
                        current_ip = x['local_host']
                        break
                        
                    epoch = float(start['timestamp']['timesecs'])
                    for interval in content['intervals']:
                        timestamp = int(epoch + float(interval['sum']['start']))
                        snapshot = time_series.setdefault(timestamp, dict())

                        for stream in interval['streams']:
                            snapshot[connections[stream['socket']]] = metrics(
                                **{k: int(float(v)) for k, v in stream.items() if k in metrics._fields}
                            )

    # drop intervals with inconsistent snapshots
    known_items = set().union(*(x.keys() for x in time_series.values()))
    for time in sorted(list(time_series.keys())):
        for flow in known_items:
            if not flow in time_series[time]:
                time_series[time][flow] = metrics(bytes=0, snd_cwnd=0, rtt=0, retransmits=0)
                #print("No information about flow")
    time_series = {k: v for k, v in time_series.items() if v.keys() >= known_items}
    #print(time_series)
    if not time_series:
        print("DBG: ERROR! raising RuntimeError, empty series")
        raise RuntimeError('Collected empty series!')
    print("DBG: end of parse_iperf, as expected")
    return time_series


def apply_series_per_interval(func, series):
    # series has at least one snapshot
    # each snapshot has the same set of items

    # get a random metric value to use as a template
    template = next(iter(next(iter(series.values())).values()))

    return {
        interval: template._make(map(func, zip(*snapshot.values())))
        for interval, snapshot in series.items()
    }


def apply_series_per_item(func, series):
    # series has at least one snapshot
    # each snapshot has the same set of items

    # get a random metric value to use as a template
    template = next(iter(next(iter(series.values())).values()))

    return {
        item: template._make(
            map(func, zip(*(x[item] for x in series.values())))
        ) for item in next(iter(series.values())).keys()
    }


def apply_per_entry(func, entries):
    # there is at least one entry in the list
    return next(iter(entries))._make(map(func, zip(*entries)))

class Flow:
    def __init__(self, src_ip, src_port, dst_ip, dst_port, start_time = '', route_number = 0, bw = 0):
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.subflows = []
        self.start_time = start_time
        self.route_number = route_number
        self.bw = bw

    def equal(self, src_ip, src_port, dst_ip, dst_port):
        if self.src_ip == src_ip and\
            self.src_port == src_port and\
            self.dst_ip == dst_ip and\
            self.dst_port == dst_port or\
            self.src_ip == dst_ip and\
            self.src_port == dst_port and\
            self.dst_ip == src_ip and\
            self.dst_port == dst_port:
            return True
        else:
            return False

    def add_subflow(self, src_ip, src_port, dst_ip, dst_port, start_time = '', route_number = 0, bw = 0):
        sub = None
        for subflow in self.subflows:
            if subflow.equal(src_ip, src_port, dst_ip, dst_port):
                sub = subflow
                break
        if sub:
            return
        sub = Flow(src_ip, src_port, dst_ip, dst_port, start_time, route_number, bw)
        self.subflows.append(sub)

    def print(self):
        if self.subflows:
            print("Parent {} {} {} {}".format(self.src_ip, self.src_port, self.dst_ip, self.dst_port))
            for sub in self.subflows:
                sub.print()
        else:
            print("Subflow {} {} {} {}".format(self.src_ip, self.src_port, self.dst_ip, self.dst_port))
            print("    Time {} Route {} Bw {}".format(self.start_time, self.route_number, self.bw))
        print("")

def watch_results(test_folder, flows):
    import re
    watch_file = open(test_folder/'1234_result.txt', 'rt')
    lines = watch_file.readlines()

    for flow in flows:
        for subflow in flow.subflows:
            src_ip = 'nw_src={}'.format(subflow.src_ip)
            dst_ip = 'nw_dst={}'.format(subflow.dst_ip)
            src_port = 'tp_src={}'.format(subflow.src_port)
            dst_port = 'tp_dst={}'.format(subflow.dst_port)
            last_bytes = 0
            rates = []
            for line in lines:
                if src_ip in line and\
                   dst_ip in line and\
                   src_port in line and\
                   dst_port in line:
                    m = re.search('bytes=([0-9]*)', line)
                    if m:
                        rates.append(int(m.group(1)) - last_bytes)
                        last_bytes = int(m.group(1))
            subflow.rates = rates


def runos_results(test_folder):
    flows = []
    runos_file = open(test_folder/'runos_result.txt', 'rt')
    lines = runos_file.readlines()
    i = 0
    while i < len(lines):
        if lines[i] == '\n':
            i += 1
            continue

        flow = None
        cols = lines[i].split()
        #Parent flow src_ip dst_ip src_port dst_port
        for f in flows:
            if f.equal(cols[2], cols[4], cols[3], cols[5]):
                flow = f
                break
        if not flow:
            flow = Flow(cols[2], cols[4], cols[3], cols[5])
            flows.append(flow)

        i += 1
        #RouteBandwidth <int> FlowRemainingBandwidth <int>
        cols = lines[i].split()
        bw = int(cols[-1]) #TODO right bw
        
        i += 1
        #RouteNumber <int> Timestamp <WeekDay> <Month> <Day> <Time> <Year>
        cols = lines[i].split()
        time = cols[-2]
        route_number = int(cols[1])

        i += 1
        #Subflow src_ip dst_ip src_port dst_port
        cols = lines[i].split()
        flow.add_subflow(cols[1], cols[3], cols[2], cols[4], time, route_number, bw)

        i += 1

    return flows

def collect_statistics(test_folder):
    stats = dict()
    print("DBG: collecting folder {}".format(test_folder))
    try:
        series = parse_iperf(test_folder/'iperf')
    except Exception as e:
        print("DBG: GOT EXCEPTION {}".format(e) )
    runos_flows = runos_results(test_folder)
    watch_results(test_folder, runos_flows)
    #print("DBG: parsed iperf in {}".format(test_folder))
    stats['exp_length'] = len(series)
    #print("DBG: stage 1")
    total_loads = apply_series_per_interval(sum, series)
    stats['total_load_mean'] = numpy.mean(list(8 * x.bytes for x in total_loads.values()))
    stats['total_load_percentiles'] = numpy.percentile(list(8 * x.bytes for x in total_loads.values()), range(10, 101, 10)).tolist()
    #print("DBG: stage 2")
    flows = []
    flow_means = apply_series_per_item(numpy.mean, series)
    flow_min = apply_series_per_item(numpy.min, series)
    flow_max = apply_series_per_item(numpy.max, series)
    time_min = min(list(series.keys()))
    for flow in flow_means:
        new_flow = {}
        new_flow['client_ip'] = flow.local_host
        new_flow['client_port'] = flow.local_port
        new_flow['server_ip'] = flow.remote_host
        new_flow['server_port'] = flow.remote_port
        #print(flow)
        new_flow['mean_rate'] = flow_means[flow].bytes
        new_flow['min_rate'] = flow_min[flow].bytes
        new_flow['max_rate'] = flow_max[flow].bytes
        new_flow['rates'] = []
        #print(flow_means[flow])
        #print(flow_min[flow])
        #print(flow_max[flow])
        for time in sorted(list(series.keys())):
            #print(time - time_min, series[time][flow])
            if not flow in series[time].keys():
                print("No time")
            new_flow['rates'].append(series[time][flow].bytes)

        start = 0
        finish = -1
        while new_flow['rates'][start] == 0:
            start += 1
        while new_flow['rates'][finish] == 0:
            finish -= 1
        #true_rates = new_flow['rates'][start:min(finish+1, -1)] 
        true_rates = new_flow['rates'][start:min(finish, -2)] 
        if len(true_rates):
            new_flow['mean_rate'] = sum(true_rates) / len(true_rates)
            new_flow['min_rate'] = min(true_rates)
            new_flow['max_rate'] = max(true_rates)

        for f in runos_flows:
            if f.equal(flow.local_host, str(flow.local_port), flow.remote_host, str(flow.remote_port)):
                new_flow['subflows'] = f.subflows
        flows.append(new_flow)
        #print(new_flow)

    stats['flow_percentiles'] = numpy.percentile(list(8 * x.bytes for x in flow_means.values()), range(10, 101, 10)).tolist()
    # flow_deviations = apply_series_per_item(numpy.std, series)
    # stats['average_deviation'] = numpy.mean(list(v.bytes/flow_means[k].bytes for k, v in flow_deviations.items()))
    stats['empty_flows'] = sum(x.bytes == 0 for x in flow_means.values()) / len(flow_means)

    itf_series = parse_collectd(test_folder/'csv.tar.gz')
    itf_series = dict(x for x in itf_series.items() if x[0] in series)
    if len(itf_series) != len(series) or not itf_series:
        raise RuntimeError('inconsistent stats')

    link_utilization = apply_series_per_item(numpy.mean, itf_series)
    stats['link_util_mean'] = numpy.mean(list(x.octets_rx / (10 ** 9) for x in link_utilization.values()))
    stats['overloaded_links'] = sum(x.octets_tx > 900 * (10**6) for x in link_utilization.values())
    stats['overloaded_links'] /= len(link_utilization)
    #print("DBG: trying to open/create test_stat.json in {}".format(test_folder))
    with open(str(test_folder/'test_stat.json'), 'wt') as fd:
        json.dump(stats, fd)
    return flows


def analyze_results(result_directory):
    result_folder = pathlib.Path("results/" + result_directory)
    flows = collect_statistics(result_folder)
    print("Analyzed " + result_directory)
    return flows

def get_topo(topo_name):
    with open("app/experiment/topo/" + topo_name, 'rb') as fp:
        graph = pickle.load(fp)
        graph = nx.Graph(graph)
        return graph
    return None

if __name__ == '__main__':

    result_folder = pathlib.Path('results')

    test_folders = set()
    pattern = re.compile('^[0-9A-Fa-f]{40}$')
    for folder in result_folder.iterdir():
        if folder.is_dir() and pattern.match(str(folder.name)):
            test_folders.add(folder)

    # run collector
    failed_folders = set()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        jobs = {executor.submit(collect_statistics, x): x for x in test_folders if not (x/'test_stat.json').is_file()}
        failed_folders = set(jobs[x] for x in concurrent.futures.as_completed(jobs) if x.exception())

    for x in failed_folders:
        print('Failed to handle {}'.format(x))

    # collect attributes
    test_cases = list()
    for x in (test_folders - failed_folders):
        with open(str(x/'test_config.json')) as fd:
            test_config = json.load(fd)
        with open(str(x/'test_stat.json')) as fd:
            test_stat = json.load(fd)
        attr_dict = dict(**test_config, **test_stat)
        test_cases.append(attr_dict)

    # check each test case has the same attributes
    attr_set = set(next(iter(test_cases)).keys())
    if any(x.keys() ^ attr_set for x in test_cases):
        raise RuntimeError('inconsistent test case')

    import test_series

    # dump aggregated statistics to a single file
    series = test_series.TestSeries(*attr_set)
    for attr_dict in test_cases:
        entry = series.template()._replace(**attr_dict)
        series.probes.append(entry)
    series.dump_json('aggregate.json')

