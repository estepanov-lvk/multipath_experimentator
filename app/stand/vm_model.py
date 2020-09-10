#!/usr/bin/env python3

from app import db, login
from app.stand.connections import conn_config
import fabric

class VM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vmname = db.Column(db.String(20), index=True, unique=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    vm_ip = db.Column(db.String(15), index=True, unique=True)
    username = db.Column(db.String(20), index=False, unique=False)
    identity_file = db.Column(db.String(40), index=False, unique=False)

    def __repr__(self):
        return '<VM {}>'.format(self.vmname)

    def update_state(self):
        import os
        self.state = "Доступна" if os.system("ping -c 1 " + self.vm_ip) is 0 else "Не доступна"

