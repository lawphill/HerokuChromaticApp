from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

print "App was called"

from app import views
