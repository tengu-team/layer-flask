import os

from charms.reactive import (
    set_state,
)

from charmhelpers.core import hookenv
from charmhelpers.core import host
from subprocess import call, Popen

config = hookenv.config()

def install_dependencies(pathWheelhouse, pathRequirements):
	call(["pip", "install", "--no-index", "--find-links=" + pathWheelhouse, "-r", pathRequirements])

def start_api(path, app, port):
	if config["nginx"]:
		start_api_gunicorn(path, app, port)
	else:		
		path = path.rstrip('/')
		info = path.rsplit('/', 1)
		Popen(["python", info[1]])	
		set_state('flask.running')

def start_api_gunicorn(path, app, port):
	saveWdir = os.getcwd()
	path = path.rstrip('/')
	#info[0] = path to project
	#info[1] = main
	info = path.rsplit('/', 1)
	#remove .py from main
	main = info[1].split('.', 1)[0] 

	file = open(info[0] + "/wsgi.py", "w")
	file.write("from " + main + " import " + app + "\n")
	file.write('if __name__ == "__main__":' + "\n")
	file.write('    ' + app + '.run()')
	file.close()

	os.chdir(info[0])
	Popen(["gunicorn", "--bind", "0.0.0.0:" + str(port), "wsgi:" + app])
	os.chdir(saveWdir)
	set_state('flask.running')