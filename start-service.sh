#! /bin/zsh
source ${HOME}/.bashrc

cd /home/es4140/proj1-3/webserver
export FLASK_ENV=development
source ~/.virtualenvs/dbproj/bin/activate
pip3 install -r requirements.txt
flask run --host=0.0.0.0 --port=8111
