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

from subprocess import call

config = hookenv.config()

@hook('install')
def install():
	saveWdir = os.getcwd()
	os.chdir('/home/ubuntu')
	url = "https://bootstrap.pypa.io/get-pip.py"
	filename = url.split("/")[-1]
	with open(filename, "wb") as f:
		r = requests.get(url)
		f.write(r.content)
	call(['python', 'get-pip.py'])
	for pkg in ['Flask', 'gunicorn', 'nginx']:
		call(["pip", "install", pkg])
	os.chdir(saveWdir)
	set_state('flask.installed')
	if config["nginx"]:
		set_state('nginx.install')

@when('website.available')
def configure_website(website):
	hookenv.log("Website available")
	website.configure(port=hookenv.config('port'))

@when('nginx.available', 'nginx.install', 'flask.running')
@when_not('flask.nginx.installed')
def start_nginx():
	hookenv.log("Configuring site for nginx")
	configure_site('default', 'gunicornhost.conf')
	set_state('flask.nginx.installed')
	status_set('active', 'Ready')

@hook('config-changed')
def config_changed():
	if config.changed("nginx"):
		if config["nginx"]:
			set_state('nginx.install')