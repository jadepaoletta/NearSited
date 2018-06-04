from flask import Flask
from flask.ext.emails import Message


app = Flask(__name__)
app.config = {'EMAIL_HOST': 'localhost', 'EMAIL_PORT': 25, 'EMAIL_TIMEOUT': 10}
app.secret_key = "ABC"


message = Message(html='<html><p>Hi! ...',
                  subject="Party today",
                  mail_from=("John Brown", "jadepaoletta27@gmail.com"))

r = message.send(to=("Nick Jackson", "jadepaoletta27@gmail.com"))

