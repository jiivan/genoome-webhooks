import os
import subprocess
from flask import Flask
from flask import request
app = Flask(__name__)

#if not app.debug:
#    import logging
#    from logging.handler import RotatingFileHandler
#    file_handler = RotatingFileHandler(
#        '/var/log/'
#    )


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
        if source_branch == 'dev' and dest_branch == 'dest':
            _dev_deploy_frontend()
        elif dest_branch == 'master' and source_branch != 'dev':
            _deploy_frontend()

if __name__ == '__main__':
    app.debug = True
    app.run()
