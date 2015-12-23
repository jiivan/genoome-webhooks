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

#if not app.debug:
#    import logging
#    from logging.handler import RotatingFileHandler
#    file_handler = RotatingFileHandler(
#        '/var/log/'
#    )


def deploy(repository, branch_name):
    print('In deploy...')
    env = {}
    env['GIT_REPOSITORY'] = settings_secret.GITHUB_REPOSITORIES[repository]
    env['GIT_BRANCH'] = branch_name
    try:
        env.update(settings_secret.DEPLOY_ENVIRONMENTS[branch_name])
    except KeyError:
        print('Ignoring branch: %s' % branch_name)
        return

    cmd = ['/opt/genoome/genoome-deploy/deploy.sh']
    subprocess.call(cmd, env=env)


def ping(data):
    """When you create a new webhook, we'll send you a simple ping event to let you know you've set up the webhook correctly.
    https://developer.github.com/webhooks/#ping-event"""

    print('PING: %s %s' % (data['zen'], data['hook_id']))
    print('HOOK: %s' % data['hook'])
    return 'PONG'


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
    github_event = request.headers['X-GitHub-Event']
    if github_event == 'ping':
        return ping(request.get_json())
    if github_event != 'push':
        print('Invalid event: %s' % github_event)
        return "INVALID EVENT"

    data = request.get_json()
    if data is None:
        print('No data in request')
        return "NO DATA"
    repository = data['repository']['full_name']

    github_sig = request.headers['X-Hub-Signature']
    my_sig = 'sha1=%s' % hmac.new(settings_secret.GITHUB_SECRETS[repository].encode('utf-8'), request.data, hashlib.sha1).hexdigest()
    if not hmac.compare_digest(my_sig, github_sig):
        print('Invalid sig: %s' % github_sig)
        return "INVALID SIG"

    # branch_name from "ref": "refs/heads/<branch_name>"
    branch_name = data['ref'].rsplit('/', 1)[-1]
    deploy(repository, branch_name)
    return "OK"


@app.route('/test')
def test():
    #deploy('jiivan/genoomy', 'dev_deploy')
    return 'OK'


if __name__ == '__main__':
    app.run()
