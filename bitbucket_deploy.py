import concurrent.futures
import hashlib
import hmac
import os
import subprocess

#from celery import Celery
from flask import Flask
from flask import request

import settings_secret

app = Flask(__name__)
app.debug = True
executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)

#if not app.debug:
#    import logging
#    from logging.handler import RotatingFileHandler
#    file_handler = RotatingFileHandler(
#        '/var/log/'
#    )


def deploy(repository, branch_name):
    env = {}
    env['GIT_REPOSITORY'] = settings_secret.GITHUB_REPOSITORIES[repository]
    env['GIT_BRANCH'] = branch_name
    env.update(settings_secret.DEPLOY_ENVIRONMENTS[branch_name])

    cmd = ['/opt/genoome/genoome/genoome/deploy.sh']
    subprocess.call(cmd, env=env)


@app.route('/frontend-deploy', methods=['POST'])
def frontend_deploy():
    data = request.get_json()
    if request.method == 'POST':
        source_branch = data['pullrequest']['source']['branch']
        dest_branch = data['pullrequest']['destination']['branch']
        if dest_branch == 'master' and source_branch != 'dev':
            #XXX
            pass
    return 'OK'


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers['X-GitHub-Event'] != 'push':
        return "INVALID EVENT"

    data = request.get_json()
    repository = data['repository']['full_name']

    github_sig = request.headers['X-Hub-Signature']
    my_sig = 'sha1=%s' % hmac.new(settings_secret.GITHUB_SECRETS[repository].encode('utf-8'), request.data, hashlib.sha1).hexdigest()
    if not hmac.compare_digest(my_sig, github_sig):
        return "INVALID SIG"

    # branch_name from "ref": "refs/heads/<branch_name>"
    branch_name = data['ref'].rsplit('/', 1)[-1]
    executor.submit(deploy, repository, branch_name)
    return "OK"


@app.route('/test')
def test():
    #deploy('jiivan/genoomy', 'dev_deploy')
    return 'OK'


if __name__ == '__main__':
    app.run()
    executor.shutdown(wait=False)
