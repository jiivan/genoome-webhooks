#!/bin/bash

PYPATH=$VENVPATH/bin/python;
GULPPATH=$VENVPATH/bin/gulp;

source $VENVPATH/bin/activate;
cd $ROOT_DIR/genoome/genoome/ && sudo git checkout -- . && \
git pull $GIT_REPOSITORY $GIT_BRANCH && \
cd $ROOT_DIR/genoome/ && \
npm install && \
./node_modules/.bin/bower install && \
$GULPPATH dist && \
cd $ROOT_DIR/genoome/genoome/ && \
$PYPATH ./manage.py collectstatic --noinput && \
sudo touch $VASSAL_INI && \
sudo chown -R ubuntu:www-data $ROOT_DIR/genoome/genoome/assets/;

echo 'Success';
