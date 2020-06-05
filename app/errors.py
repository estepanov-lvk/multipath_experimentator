from flask import render_template
from app import app, db
from app.telebot.mastermind import send_message

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    send_message("500 error")
    return render_template('500.html'), 500
