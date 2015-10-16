import os
import subprocess

os.chdir(os.path.expanduser('~/Documents/genoome/genoome/genoome'))
subprocess.call(['git status'], shell=True)
