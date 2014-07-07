from flask import Flask

print "Init file was called"
app = Flask(__name__)
app.config.from_object('config')

print "App configured"

import views

print "Views was imported"
