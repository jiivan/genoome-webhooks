import os
import subprocess

#from celery import Celery
from flask import Flask
from flask import request
app = Flask(__name__)
app.debug = True

#if not app.debug:
#    import logging
#    from logging.handler import RotatingFileHandler
#    file_handler = RotatingFileHandler(
#        '/var/log/'
#    )
CELERY_BROKER_URL = 'redis://localhost:6379/1'

#def make_celery(app):
#    celery = Celery(app.import_name, broker=CELERY_BROKER_URL)
#    TaskBase = celery.Task
#    class ContextTask(TaskBase):
#        abstract = True
#        def __call__(self, *args, **kwargs):
#            with app.app_context():
#                return TaskBase.__call(*args, **kwargs)
#    celery.Task = ContextTask
#    return celery

#celery_app = make_celery(app)

#@celery_app.task()
def _dev_deploy_frontend():
    subprocess.call(['/opt/dev_genoome/genoome/genoome/dev_frontend_deploy.sh'])

def _deploy_frontend():
    subprocess.call(['/opt/genoome/genoome/genoome/frontend_deploy.sh'])

@app.route('/frontend-deploy', methods=['POST'])
def frontend_deploy():
    data = request.get_json()
    if request.method == 'POST':
        source_branch = data['pullrequest']['source']['branch']
        dest_branch = data['pullrequest']['destination']['branch']
        if dest_branch == 'master' and source_branch != 'dev':
            _deploy_frontend()
    return 'OK'


@app.route('/dev-deploy', methods=['POST'])
def dev_deploy():
    if request.method == 'POST' and request.headers['X-GitHub-Event'] == 'push':
        _dev_deploy_frontend()
    return "OK"


@app.route('/test')
def test():
    return 'OK'


if __name__ == '__main__':
    app.debug = True
    app.run()
