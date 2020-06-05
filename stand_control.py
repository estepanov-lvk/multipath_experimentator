from app import app, db
from app.models import User, Server, VM, Experiment

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Server': Server, 'VM': VM, 'Experiment': Experiment}
