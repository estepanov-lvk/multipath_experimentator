from app import db

class Experiment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(10), index=True)
    model = db.Column(db.String(10), index=True)
    subflow = db.Column(db.Integer, index=True)
    topo = db.Column(db.String(20), index=True)
    poles = db.Column(db.Integer, index=True)
    flows = db.Column(db.Integer, index=True)
    poles_seed = db.Column(db.Integer, index=True)
    routes_seed = db.Column(db.Integer, index=True)
    cc = db.Column(db.String(20), index=True)
    protocol = db.Column(db.String(20), index=True)
    distribution = db.Column(db.String(20), index=True)
    time = db.Column(db.Integer, index=True)
    probe = db.Column(db.Integer, index=True)

    completed = db.Column(db.Boolean, index=True)

    def __repr__(self):
        return '<Experiment {}>'.format(self.id)

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
        unique_str += str(self.protocol)
        unique_str += str(self.distribution)
        unique_str += str(self.time)
        unique_str += str(self.probe)
        return hashlib.sha1(unique_str.encode()).hexdigest()

class Topo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), index = True, unique=True)
    nodes = db.Column(db.Integer, index = True)
    edges = db.Column(db.Integer, index = True)
