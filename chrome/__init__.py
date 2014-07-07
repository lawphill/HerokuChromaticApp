from flask import Flask

print "Init file was called"
app = Flask(__name__)
app.config.from_object('config')

print "App configured"

from chrome import views

print "Views was imported"
