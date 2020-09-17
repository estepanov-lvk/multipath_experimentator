import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #Experiment parameters
    MODE_CHOICES = ['single', 'mp', 'mixed']
    MODEL_CHOICES = ['gspf', 'mcmf', 'rnh', 'ihf']
    CC_CHOICES = ['cubic']
    DISTRIBUTION_CHOICES = ['weibull', 'uniform', 'normal']

    PROTOCOL_CHOICES = ['mptcp', 'fdmp']
