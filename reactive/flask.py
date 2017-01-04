import os
import requests

from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import (
	status_set,
	open_port,
	config,
)

from charmhelpers.contrib.python.packages import pip_install, pip_install_requirements
from charms.reactive import hook, when, when_not, set_state, remove_state

from charms.layer.nginx import configure_site
from charms.layer.flaskhelpers import restart_api

from subprocess import call

config = hookenv.config()

@when_not('flask.installed')
def install():
	if not os.path.exists("/home/ubuntu/flask-config"):
		touch('/home/ubuntu/flask-config')
	for pkg in ['Flask', 'gunicorn', 'nginx']:
		pip_install(pkg)
	set_state('flask.installed')
	if config["nginx"]:
		set_state('nginx.install')
	else:
		set_state('nginx.stop')

@when('nginx.stop', 'nginx.available')
def stop_nginx():
	call(['service', 'nginx', 'stop'])
	remove_state('nginx.stop')

@when('website.available')
def configure_website(website):
	hookenv.log("Website available")
	website.configure(port=hookenv.config('port'))

@when('nginx.available', 'nginx.install', 'flask.running')
@when_not('flask.nginx.installed')
def start_nginx():
	hookenv.log("Configuring site for nginx")
	configure_site('default', 'gunicornhost.conf', flask_port=config['flask-port'])
	set_state('flask.nginx.installed')
	status_set('active', 'Ready')

@when('config.changed.nginx')
def config_changed_nginx():
	if config["nginx"]:
		set_state('nginx.install')

@when('config.changed.flask-port', 'flask.installed')
def config_changed_flask_port():
	if config.changed('flask-port') and config["nginx"]:
		hookenv.log("Port change detected")
		hookenv.log("Restarting API")
		remove_state('flask.nginx.installed')
		#remove old port connections
		call(["fuser", "-k", str(config.previous('flask-port')) + "/tcp"])
		#remove new port connections
		call(["fuser", "-k", str(config['flask-port']) + "/tcp"])
		#start api again
		restart_api(config['flask-port'])

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)