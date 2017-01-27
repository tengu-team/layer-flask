
# layer-flask
This layer allows configuration for Flask applications, with or without gunicorn and nginx deployment.

# Usage

Include this layer in your`layer.yaml`

```
layer:flask
```
The Flask layer allows you to install dependencies for the Flask application via wheelhouse.

Example:

```python
from charms.layer.flaskhelpers import install_dependencies

@when_not(app.installed)
def install():
    install_dependencies(project_path + "/wheelhouse", project_path + "/requirements.txt")
    set_state('app.installed')
```

The flask layer will set the `flask.installed` state when installed and can be used as an indicator to start the Flask application. The `start_api()` function is used to tell the flask layer to launch the application. it takes three arguments:
`start_api(PATH_TO_PROJECT_MAIN_FILE, APP_OBJECT_NAME, FLASK_PORT)`. The `APP_OBJECT_NAME` is nothing more than the name you gave your app object in your application `app = Flask(__name__)`.

Example:

```python
@when('flask.installed')
@when_not('app.running')
def start_app():
   start_api(project_path + "/server.py", "app", config["flask-port"])
   set_state('app.running')
```


## Run Flask from app.run()
This mode is intended for development purposes. To run in this mode, deploy your charm with configuration option `nginx: False`. The API will be running on port 5000.

## Run Flask with Gunicorn and NGINX
To run in this mode, deploy your charm with configuration option `nginx: True`.
The Flask layer utilizes `layer:nginx` [Repo](https://github.com/battlemidget/juju-layer-nginx) and therefor requires a `site.toml` file for additional configuration. 

The `site.toml` needs at least one configuration parameter:
```
"server_name" = "_"
```
The API will be running on the port specified on 


## Authors

This software was created in the [IBCN research group](https://www.ibcn.intec.ugent.be/) of [Ghent University](http://www.ugent.be/en) in Belgium. This software is used in [Tengu](http://tengu.intec.ugent.be), a project that aims to make experimenting with data frameworks and tools as easy as possible.

 - Sander Borny <sander.borny@intec.ugent.be>