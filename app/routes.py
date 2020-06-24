from flask import render_template, redirect, flash, url_for
from flask import request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ServerAddForm
from app.forms import ServerDeleteForm, ServerEditForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Experiment, Server, ServerInterface
from werkzeug.urls import url_parse
from datetime import datetime
from app.telebot.mastermind import bot
from . import socketio
from flask_socketio import emit

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

@app.route('/stand')
@login_required
def stand():
    servers = Server.query.all()

    def insertDefaultState(elem):
        elem.state = 'Обновляется'
        return elem

    servers = list(map(insertDefaultState, servers))
    return render_template('stand.html', title='Аппаратная часть стенда', servers=servers)

def makeServerStateInfo(server):
    return {
        "serverName": server.servername,
        "serverState": server.state
    }

@socketio.on('updateServerState', namespace='/test')
def updateServerState(msg):
    for serverName in msg:
        server_obj = Server.query.filter_by(servername=serverName).first()
        if server_obj is None:
            return
        server_obj.update_state()
        emit("updatedServerState", makeServerStateInfo(server_obj))

@app.route('/server_add', methods=['GET', 'POST'])
@login_required
def server_add():
    form = ServerAddForm()
    interfaces = form.interfaces

    if form.validate_on_submit():
        server = Server(servername = form.servername.data,
                        server_ip = form.server_ip.data)
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
                db.session.delete(intf)
        db.session.commit()
        flash('Информация о сервере успешно обновлена')
        return redirect(url_for('stand'))
    elif request.method == 'GET':
        form.servername.data = server.servername
        form.server_ip.data = server.server_ip
        for intf in list(server.interfaces):
            form.interfaces.append_entry(intf)
    return render_template('server_edit.html', title='Редактирование сервера', form=form)
