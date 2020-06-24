#!/usr/bin/env python3

from app import db, login

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servername = db.Column(db.String(20), index=True, unique=True)
    server_ip = db.Column(db.String(15), index=True, unique=True)
    vms = db.relationship('VM', backref='server', lazy='dynamic')
    interfaces = db.relationship('ServerInterface', backref='server', lazy='dynamic')

    def __repr__(self):
        return '<Server {}>'.format(self.servername)

    def update_state(self):
        import os
        self.state = "Доступен" if os.system("ping -c 1 " + self.server_ip) is 0 else "Не доступен"


class ServerInterface(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    interface_name = db.Column(db.String(20), index=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))

    def __repr__(self):
        return '<Server interface {}>'.format(self.interface_name)


