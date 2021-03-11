from flask import render_template, redirect, flash, url_for
from flask import request
from app import app, db, tester
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ServerAddForm
from app.forms import ServerDeleteForm, ServerEditForm
from app.forms import ConnectionAddForm, ConnectionDeleteForm
from app.forms import VMAddForm, VMDeleteForm, VMEditForm
from app.forms import ExperimentAddForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Server, ServerInterface, ServerConnection, VM, Experiment
from werkzeug.urls import url_parse
from datetime import datetime
from app.telebot.mastermind import bot
from . import socketio
from flask_socketio import emit
from app.experiment.grabber import get_topo
from app.experiment.tester import vm_config

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Evgeniy'}
    vms = [
        {
            'info': {'name': 'w1loader1'},
            'condition': 'active'
        },
        {
            'info': {'name': 'w1loader2'},
            'condition': 'active'
        },
        {
            'info': {'name': 'w3loader1'},
            'condition': 'active'
        },
        {
            'info': {'name': 'w3loader2'},
            'condition': 'down'
        }
    ]
    return render_template('index.html', title = 'Experiment Control', vms = vms)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильное имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title = 'Вход в систему', form = form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, Вы новый зарегистрированный пользователь!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/experiment/<experimentid>')
@login_required
def exp_info(experimentid):
    exp = Experiment.query.filter_by(id=experimentid).first_or_404()
    return render_template('experiment.html', experiment=exp)

@app.route('/experiment_remove/<experimentid>')
@login_required
def exp_del(experimentid):
    import shutil
    exp = Experiment.query.filter_by(id=experimentid).first_or_404()
    
    #remove the results directory
    result_directory = "results/" + exp.sha_hash()
    shutil.rmtree(result_directory, ignore_errors=True)

    #remove experiments from database
    db.session.delete(exp)
    db.session.commit()

    return redirect(url_for('results'))


@app.route('/result_remove/<experimentid>')
@login_required
def res_del(experimentid):
    import shutil
    exp = Experiment.query.filter_by(id=experimentid).first_or_404()

    #remove the results directory
    result_directory = "results/" + exp.sha_hash()
    shutil.rmtree(result_directory, ignore_errors=True)

    exp.completed = False
    db.session.commit()
    return redirect(url_for('results'))

@app.route('/experiments')
@login_required
def experiments():
    exps = tester.waiting_experiments()
    return render_template('experiments.html', title='Эксперименты', exps=exps)

@app.route('/result/<experimentid>')
@login_required
def exp_result(experimentid):
    from app.experiment.grabber import analyze_results
    exp = Experiment.query.filter_by(id=experimentid).first_or_404()
    flows = analyze_results(exp.sha_hash())
    return render_template('result.html', experiment=exp, flows = flows)

@app.route('/result/<experimentid>/topo')
@login_required
def exp_topo(experimentid):
    exp = Experiment.query.filter_by(id=experimentid).first_or_404()
    topo = get_topo(exp.topo)
    nodes = topo.nodes()
    edges = topo.edges()

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
    return render_template('result_topo.html', experiment=exp, nodes=nodes, edges=edges,
                            classes=classes)

@app.route('/results')
@login_required
def results():
    exps = Experiment.query.filter_by(completed = True).all()
    return render_template('results.html', title='Результаты', exps=exps)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    series = [
        {'creator': user, 'id': 1},
        {'creator': user, 'id': 2}
    ]
    return render_template('user.html', user=user, series=series)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Ваши изменения были сохранены.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактировать профиль', form=form)

def make_connections():
    connections = []
    conns = ServerConnection.query.all()
    for conn in conns:
        new_conn = {}
        int1Model = ServerInterface.query.filter_by(id=conn.int1)[0]
        int2Model = ServerInterface.query.filter_by(id=conn.int2)[0]
        srv1Model = Server.query.filter_by(id=int1Model.server_id)[0]
        srv2Model = Server.query.filter_by(id=int2Model.server_id)[0]
        new_conn['serv1'] = srv1Model.servername
        new_conn['int1'] = int1Model.interface_name
        new_conn['int2'] = int2Model.interface_name
        new_conn['serv2'] = srv2Model.servername
        connections.append(new_conn)
    return connections

@app.route('/stand')
@login_required
def stand():
    servers = Server.query.all()
    vms = VM.query.all()

    def insertDefaultState(elem):
        elem.state = 'Обновляется'
        return elem

    def insertServerName(elem):
        elem.servername = Server.query.filter_by(id=elem.server_id).first().servername
        return elem

    servers = list(map(insertDefaultState, servers))
    vms = list(map(insertServerName, vms))
    vms = list(map(insertDefaultState, vms))
    connections = make_connections()
    return render_template('stand.html', title='Аппаратная часть стенда', servers=servers, connections=connections, vms=vms)

def makeServerStateInfo(server):
    return {
        "serverName": server.servername,
        "serverState": server.state
    }

@socketio.on('updateTesterState', namespace='/test')
def updateTesterState(msg):
    reply = tester.form_state()
    emit('updatedTesterState', reply)
    print("update tester state")


@socketio.on('updateServerState', namespace='/test')
def updateServerState(msg):
    for serverName in msg:
        server_obj = Server.query.filter_by(servername=serverName).first()
        if server_obj is None:
            return
        server_obj.update_state()
        emit("updatedServerState", makeServerStateInfo(server_obj))

def makeVMStateInfo(vm):
    return {
        "vmName": vm.vmname,
        "vmState": vm.state
    }

@socketio.on('updateVMState', namespace='/test')
def updateVMState(msg):
    for vmName in msg:
        vm_obj = VM.query.filter_by(vmname=vmName).first()
        if vm_obj is None:
            return
        vm_obj.update_state()
        emit("updatedVMState", makeVMStateInfo(vm_obj))



@socketio.on('updateInterfacesState', namespace='/test')
def updateInterfaceState(msg):
    serverName = msg['serverName']
    interfaces = msg['interfaces']

    server_obj = Server.query.filter_by(servername=serverName).first()
    if server_obj is None:
        return

    reply = {}
    reply['serverName'] = serverName
    reply['interfaces'] = {}

    for intf in server_obj.interfaces:
        state = intf.update_state()
        reply['interfaces'][intf.interface_name] = state

    emit('updatedInterfacesState', reply)

def get_identity_file(servername):
    return "~/.ssh/fdmp_stand"

def make_list(s):
    a = eval(s)
    if (type(a) != type(list()) and type(a) != type(tuple())):
        a = [a]
    return a

def find_probe(x):
    return len(Experiment.query.filter_by(
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
                protocol = x[10],
                time = x[11]).all())


def generate_experiments(form):
    import itertools

    new_experiments = []

    time_list = [int(form.time.data)]
    print(type(time_list))
    print(time_list)
    print(time_list[0])
    for x in itertools.product(
            form.mode.data,
            form.model.data,
            make_list(form.subflow.data),
            form.cc.data,
            form.distribution.data,
            form.topos.data,
            make_list(form.poles.data),
            make_list(form.flows.data),
            make_list(form.poles_seed.data),
            make_list(form.routes_seed.data),
            form.protocol.data,
            make_list(form.time.data)
            ):
        #checks?
        
        #find the number of similar experiments
        max_probe = find_probe(x)
        for i in range(int(form.probe.data)):
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
                    protocol = x[10],
                    time = x[11],
                    probe = max_probe + i,
                    completed = False)
            new_experiments.append(experiment)

    return new_experiments

        
    

@app.route('/experiment_add', methods=['GET', 'POST'])
@login_required
def experiment_add():
    form = ExperimentAddForm()

    if form.validate_on_submit():
        exps = generate_experiments(form)
        for exp in exps:
            db.session.add(exp)
        db.session.commit()
        flash('Эксперименты в количестве {} были успешно добавлены'.format(len(exps)))
        return redirect(url_for('experiments'))
    return render_template('experiment_add.html', title='Добавление серии экспериментов', form=form)

@app.route('/server_add', methods=['GET', 'POST'])
@login_required
def server_add():
    form = ServerAddForm()
    interfaces = form.interfaces

    if form.validate_on_submit():
        server = Server(servername = form.servername.data,
                        server_ip = form.server_ip.data,
                        username = form.username.data)
        server.identity_file = get_identity_file(server.servername)
        for intf in form.interfaces.data:
            new_intf = ServerInterface(interface_name = intf['interface_name'])
            new_intf.server_id = server.id
            db.session.add(new_intf)
            db.session.commit()
            server.interfaces.append(new_intf)
        db.session.add(server)
        db.session.commit()
        flash('Сервер {} был успешно добавлен'.format(form.servername.data))
        return redirect(url_for('stand'))

    return render_template('server_add.html', title='Добавление сервера', form=form)

@app.route('/server_delete', methods=['GET', 'POST'])
@login_required
def server_delete():
    form = ServerDeleteForm()

    if form.validate_on_submit():
        server = Server.query.filter_by(servername = form.servername.data).first()
        server_interfaces = ServerInterface.query.filter_by(server_id = server.id)
        for intf in server_interfaces:
            db.session.delete(intf)
        db.session.delete(server)
        db.session.commit()
        flash('Сервер {} был успешно удален'.format(form.servername.data))
        return redirect(url_for('stand'))

    return render_template('server_delete.html', title='Удаление сервера', form=form)

@app.route('/vm_add', methods=['GET', 'POST'])
@login_required
def vm_add():
    form = VMAddForm()

    if form.validate_on_submit():
        server = Server.query.filter_by(servername=form.servername.data).first()
        vm = VM(vmname = form.vmname.data,
                vm_ip = form.vm_ip.data,
                username = form.username.data,
                server_id = server.id)
        vm.identity_file = get_identity_file(vm.vmname)
        db.session.add(vm)
        db.session.commit()
        flash('Виртуальная машина {} была успешно добавлена'.format(form.vmname.data))
        return redirect(url_for('stand'))

    servers = Server.query.all()
    serverNames = []
    for serv in servers:
        serverNames.append(serv.servername)
    form.servername.choices= [(srv, srv) for srv in serverNames]
    return render_template('vm_add.html', title='Добавление виртуальной машины', form=form)

@app.route('/vm_delete', methods=['GET', 'POST'])
@login_required
def vm_delete():
    form = VMDeleteForm()

    if form.validate_on_submit():
        vm = VM.query.filter_by(vmname = form.vmname.data).first()
        db.session.delete(vm)
        db.session.commit()
        flash('Виртуальная машина {} была успешно удалена'.format(form.vmname.data))
        return redirect(url_for('stand'))

    return render_template('vm_delete.html', title='Удаление виртуальной машины', form=form)



def get_all_interfaces(servers):
    result = {}
    for serv in servers:
        result[serv.servername] = []
        server_interfaces = ServerInterface.query.filter_by(server_id = serv.id)
        for intf in server_interfaces:
            result[serv.servername].append(intf.interface_name)
    print(result)
    return result


@app.route('/connection_add', methods=['GET', 'POST'])
@login_required
def connection_add():
    form = ConnectionAddForm()

    if form.validate_on_submit():
        if form.server1.data == form.server2.data:
            flash('Соединение не может быть между одним и тем же сервером.')
            return redirect(url_for('connection_add'))

        serv1Model = Server.query.filter_by(servername = form.server1.data)[0]
        serv2Model = Server.query.filter_by(servername = form.server2.data)[0]
        int1Model = ServerInterface.query.filter_by(server_id = serv1Model.id, interface_name = form.int1.data)[0]
        int2Model = ServerInterface.query.filter_by(server_id = serv2Model.id, interface_name = form.int2.data)[0]

        connections = ServerConnection.query.all()
        for conn in connections:
            if conn.int1 == int1Model.id and conn.int2 == int2Model.id or\
                conn.int1 == int2Model.id and conn.int2 == int1Model.id:
                flash('Такое соединение уже существует.')
                return redirect(url_for('connection_add'))

        new_conn = ServerConnection(int1 = int1Model.id,
                                    int2 = int2Model.id)
        db.session.add(new_conn)
        db.session.commit()
        flash('Новое соединение было успешно добавлено')
        return redirect(url_for('stand'))

    #add options values
    servers = Server.query.all()
    interfaces = get_all_interfaces(servers)
    serverNames = []
    for serv in servers:
        serverNames.append(serv.servername)
    form.server1.choices= [(srv, srv) for srv in serverNames]
    form.server1.default = serverNames[0]
    form.int1.choices = [(intf, intf) for intf in interfaces[serverNames[0]]]
    form.server2.choices= [(srv, srv) for srv in serverNames]
    form.server2.default = serverNames[1]
    form.int2.choices = [(intf, intf) for intf in interfaces[serverNames[1]]]
    form.process()
    return render_template('connection_add.html', title='Добавление соединения', form=form, servers = serverNames, interfaces=interfaces)

@app.route('/connection_delete', methods=['GET', 'POST'])
@login_required
def connection_delete():
    form = ConnectionDeleteForm()

    if form.validate_on_submit():
        if form.server1.data == form.server2.data:
            flash('Соединение не может быть между одним и тем же сервером.')
            return redirect(url_for('connection_delete'))

        serv1Model = Server.query.filter_by(servername = form.server1.data)[0]
        serv2Model = Server.query.filter_by(servername = form.server2.data)[0]
        int1Model = ServerInterface.query.filter_by(server_id = serv1Model.id, interface_name = form.int1.data)[0]
        int2Model = ServerInterface.query.filter_by(server_id = serv2Model.id, interface_name = form.int2.data)[0]

        connections = ServerConnection.query.all()
        for conn in connections:
            if conn.int1 == int1Model.id and conn.int2 == int2Model.id or\
                conn.int1 == int2Model.id and conn.int2 == int1Model.id:
                    db.session.delete(conn)
                    db.session.commit()
                    flash('Соединение было успешно удалено')
                    return redirect(url_for('stand'))

        flash('Такого соединения не существует')
        return redirect(url_for('stand'))

    #add options values
    servers = Server.query.all()
    interfaces = get_all_interfaces(servers)
    serverNames = []
    for serv in servers:
        serverNames.append(serv.servername)
    form.server1.choices= [(srv, srv) for srv in serverNames]
    form.server1.default = serverNames[0]
    form.int1.choices = [(intf, intf) for intf in interfaces[serverNames[0]]]
    form.server2.choices= [(srv, srv) for srv in serverNames]
    form.server2.default = serverNames[1]
    form.int2.choices = [(intf, intf) for intf in interfaces[serverNames[1]]]
    form.process()
    return render_template('connection_delete.html', title='Удаление соединения', form=form, servers = serverNames, interfaces=interfaces)


@app.route('/server_edit/<servername>', methods=['GET', 'POST'])
@login_required
def server_edit(servername):
    server = Server.query.filter_by(servername = servername).first()
    if server is None:
        flash('Не существует сервера с именем {}'.format(servername))
        return redirect(url_for('stand'))

    form = ServerEditForm(servername, server.server_ip)
    if form.validate_on_submit():
        server.servername = form.servername.data
        server.server_ip = form.server_ip.data
        server.username = form.username.data

        old_interfaces = list(server.interfaces)
        old_interface_names = set([x.interface_name for x in old_interfaces])
        new_interface_names = set([intf['interface_name'] for intf in form.interfaces.data])
        interfaces_to_delete = old_interface_names - new_interface_names
        interfaces_to_add = new_interface_names - old_interface_names
        for intf in form.interfaces.data:
            if intf['interface_name'] in interfaces_to_add:
                new_intf = ServerInterface(interface_name = intf['interface_name'])
                new_intf.server_id = server.id
                db.session.add(new_intf)
                server.interfaces.append(new_intf)

        for intf in old_interfaces:
            if intf.interface_name in interfaces_to_delete:
                for conn in ServerConnection.query.all():
                    if conn.int1 == intf.id or conn.int2 == intf.id:
                        db.session.delete(conn)
                db.session.delete(intf)
        db.session.commit()
        flash('Информация о сервере успешно обновлена')
        return redirect(url_for('stand'))
    elif request.method == 'GET':
        form.servername.data = server.servername
        form.server_ip.data = server.server_ip
        form.username.data = server.username
        for intf in list(server.interfaces):
            form.interfaces.append_entry(intf)
    return render_template('server_edit.html', title='Редактирование сервера', form=form)



@app.route('/vm_edit/<vmname>', methods=['GET', 'POST'])
@login_required
def vm_edit(vmname):
    vm = VM.query.filter_by(vmname=vmname).first()
    if vm is None:
        flash('Не существует виртуальной машины с именем {}'.format(vmname))
        return redirect(url_for('stand'))

    form = VMEditForm(vmname, vm.vm_ip)

    if form.validate_on_submit():
        vm.vmname = form.vmname.data
        vm.vm_ip = form.vm_ip.data
        vm.username = form.username.data
        serv = Server.query.filter_by(servername=form.servername.data).first()
        vm.server_id = serv.id
        db.session.commit()
        flash('Виртуальная машина {} была успешно обновлена'.format(form.vmname.data))
        return redirect(url_for('stand'))
    elif request.method == 'GET':
        form.vmname.data = vm.vmname
        form.vm_ip.data = vm.vm_ip
        form.username.data = vm.username
        servers = Server.query.all()
        serverNames = []
        for serv in servers:
            serverNames.append(serv.servername)
        form.servername.choices= [(srv, srv) for srv in serverNames]
        form.servername.data = Server.query.filter_by(id=vm.server_id).first().servername
    return render_template('vm_edit.html', title='Редактирование виртуальной машины', form=form)
