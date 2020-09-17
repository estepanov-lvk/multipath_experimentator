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

class Topo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), index = True, unique=True)
    nodes = db.Column(db.Integer, index = True)
    edges = db.Column(db.Integer, index = True)
