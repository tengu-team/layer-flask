import os
from charms.reactive import (
    set_state,
)
from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from subprocess import call, Popen

config = hookenv.config()

def install_dependencies(pathWheelhouse, pathRequirements):
    hookenv.log('Installing dependencies')
    call(["pip", "install", "--no-index", "--find-links=" + pathWheelhouse, "-r", pathRequirements])

def install_requirements(pathRequirements):
    hookenv.log('Installing dependencies')
    call(["pip", "install", "--upgrade", "-r", pathRequirements])

# Should be used by the layer including the flask layer
def start_api(path, app, port):    
    if os.path.exists("/home/ubuntu/flask/flask-config"):
        file = open("/home/ubuntu/flask/flask-config", "w")
        file.write(path + " " + app)
        file.close()        
        start(path, app, port)

# Used by the flask layer to restart when flask-port changes occur
def restart_api(port):    
    path, app = get_app_info()
    if path != "" and app != "":
        start(path, app, port)

def start(path, app, port):
    if config["nginx"]:
        start_api_gunicorn(path, app, port, config['workers'])
    else:
        path = path.rstrip('/')
        Popen(["python3", path])
        set_state('flask.running')

def start_api_gunicorn(path, app, port, workers):
    stop_api()
    path = path.rstrip('/')
    #info[0] = path to project
    #info[1] = main
    info = path.rsplit('/', 1)
    #remove .py from main
    main = info[1].split('.', 1)[0]
    if os.path.exists(info[0] + '/wsgi.py'):
        os.remove(info[0] + '/wsgi.py')
    render(source='gunicorn.wsgi',
           target=info[0] + "/wsgi.py",
           context={
                'app': app,
                'main': main,
           })
    
    render(source='unitfile',
           target='/etc/systemd/system/flask.service',
           context={
                'port': str(port),
                'pythonpath': info[0],
                'app': app,
                'workers': str(workers)
           })

    call(['systemctl', 'enable', 'flask'])
    host.service_start('flask')

def is_flask_running():
    if call(['systemctl', 'is-active', 'flask']) == 0:
        return True
    return False

def stop_api():
    if host.service_running('flask'):
        host.service_stop('flask')
        call(['systemctl', 'disable', 'flask'])
        if os.path.exists('/etc/systemd/system/flask.service'):
            os.remove('/etc/systemd/system/flask.service')

def set_workers():
    n_workers = config['workers']
    previous_workers = config.previous('workers')
    if os.path.exists("/home/ubuntu/flask/master.pid"):
        file = open('/home/ubuntu/flask/master.pid', 'r')
        pid = file.readline().strip()
        file.close()
        if is_flask_running():
            if n_workers > previous_workers:
            	while previous_workers < n_workers:
                	call(["kill", "-TTIN", pid])
                	previous_workers += 1
            elif n_workers < previous_workers:
            	while previous_workers > n_workers:
                	call(["kill", "-TTOU", pid])
                	previous_workers -= 1
        rewrite_unitfile()

def rewrite_unitfile():
    if os.path.exists('/etc/systemd/system/flask.service'):
        path, app = get_app_info()
        path = path.rstrip('/')
        pp = path.rsplit('/', 1)[0]
        render(source='unitfile',
           target='/etc/systemd/system/flask.service',
           context={
                'port': config['flask-port'],
                'pythonpath': pp,
                'app': app,
                'workers': config['workers']
           })
        call(['systemctl', "daemon-reload"])

def get_app_info():
    if os.path.exists("/home/ubuntu/flask/flask-config"):
        file = open("/home/ubuntu/flask/flask-config", "r")
        line = file.readline()
        if line != "":
            path, app = line.split()
            return path, app
    return "", ""            