#!/bin/bash -e
git-up
git checkout master
git fetch upstream
git rebase upstream/master master
git checkout hhl_changes
git merge master
source venv/bin/activate
pip install -r requirements/production.txt
./manage.py migrate
npm run build
./manage.py collectstatic --noinput
for app in locale */locale; do (cd $(dirname $app) && ../manage.py compilemessages ); done

