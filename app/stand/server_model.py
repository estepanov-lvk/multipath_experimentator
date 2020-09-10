#!/usr/bin/env python3

from app import db, login
import fabric

SSHCONFIG = "./app/stand/ssh_config"
SSHCONFIG_PATH = "./app/stand/"
conn_config = fabric.Config(runtime_ssh_path=SSHCONFIG)
conn_config.load_ssh_config()

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servername = db.Column(db.String(20), index=True, unique=True)
    server_ip = db.Column(db.String(15), index=True, unique=True)
    vms = db.relationship('VM', backref='server')
    interfaces = db.relationship('ServerInterface', backref='server')
    username = db.Column(db.String(20), index=False, unique=False)
    identity_file = db.Column(db.String(40), index=False, unique=False)

    def __repr__(self):
        return '<Server {}>'.format(self.servername)

    def update_state(self):
        import os
        self.state = "Доступен" if os.system("ping -c 1 " + self.server_ip) is 0 else "Не доступен"



class ServerInterface(db.Model):
    __tablename__ = 'serverinterface'
    id = db.Column(db.Integer, primary_key=True)
    interface_name = db.Column(db.String(20), index=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))

    def __repr__(self):
        return '<Server interface {}>'.format(self.interface_name)

    def update_state(self):
        status = 'Опущен'
        server = Server.query.filter_by(id=self.server_id).first()
        c = fabric.connection.Connection(host=server.servername, config=conn_config)

        try:
            res = c.run('cat /sys/class/net/{}/operstate'.format(self.interface_name), hide='both')
            if res.stdout.startswith('up'):
                status = 'Поднят'
        except Exception as e:
            print("EXCEPTION:    ", e)
            print(server.servername)
            print(conn_config)

        return status

class ServerConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    int1 = db.Column(db.Integer, db.ForeignKey('serverinterface.id'))
    int2 = db.Column(db.Integer, db.ForeignKey('serverinterface.id'))

    def __repr__(self):
        intModel1 = ServerInterface.query.filter_by(id=self.int1).first()
        srvModel1 = Server.query.filter_by(id=intModel1.server_id).first()
        intModel2 = ServerInterface.query.filter_by(id=self.int2).first()
        srvModel2 = Server.query.filter_by(id=intModel2.server_id).first()
        return '<Server connection {} {} --- {} {}>'.format(srvModel1.servername, intModel1.interface_name, intModel2.interface_name, srvModel2.servername)
