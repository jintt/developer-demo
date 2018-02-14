#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from fabric.api import (
    cd,
    env,
    execute,
    local,
    runs_once,
    task,
    sudo,
    settings,
)
from fabric.contrib.files import exists
from fabric.colors import (
    green,
    red,
)

env.use_ssh_config = True
env.keepalive = 60
env.deploying_commit = local('git rev-parse HEAD', capture=True)

ALL_SERVICE_IDS = [
    'dt.test',
]


SERVICES = [
    'dt.test',
]

service_id_name_map = {
    'dt.test': 'dt.test',
}


def get_service_name_by_app_ids(app_ids):
    service_names = [service_id_name_map.get(_id) for _id in app_ids]
    return filter(None, service_names)


# const define
DEPLOYMENT_PARAMS = {
    "repo": "developer",
    "remote_user": "www-data",
    "local_dir": os.path.dirname(os.path.realpath(__file__)),
    "remote_exclude": "rsync_exclude.txt",
    "requirements": "requirements.txt",
    "remote_dir": '/data/dt',
    "virtualenv": "/data/dt/.venv",
}

BASE_WHEEL_BASE_DIR = '/data/dt'
BASE_WHEEL_DIR = '%s/.wheelhouse' % BASE_WHEEL_BASE_DIR


def _get_pip_install_args():
    return ' -r %s' % DEPLOYMENT_PARAMS['requirements']


@task
def virtualenv_init(virtualenv):
    if exists(virtualenv):
        return
    sudo("virtualenv {}".format(virtualenv))
    sudo("{0}/bin/pip install --upgrade pip".format(
        virtualenv))


@task
def do_common_rsync(app_id):
    deployment_params = DEPLOYMENT_PARAMS
    execute(virtualenv_init, deployment_params['virtualenv'])
    sync_args = [
        deployment_params['local_dir'],
        deployment_params['remote_dir'],
        deployment_params['remote_user'],
        deployment_params['remote_exclude']
    ]
    execute(common_rsync, *sync_args)


@task
def common_rsync(local_dir, remote_dir, remote_user, remote_exclude):
    if not exists(remote_dir):
        sudo("mkdir -p {}".format(remote_dir))
    sudo("chown {0} -R {1}".format(env.user, remote_dir))
    commit_indicator = '.commit'

    # pylint: disable=E1129
    with open(commit_indicator, 'w') as f:
        f.write(env.deploying_commit)
    local("rsync -azq -e \"ssh -i $HOME/.ssh/id_rsa\" "
          "--progress --force --delete --delay-updates "
          "--exclude-from={0} {1}/ {5}@{3}:{2}/ "
          "--include {4}".format(
              os.path.join(local_dir, remote_exclude),
              local_dir,
              remote_dir,
              env.host_string,
              commit_indicator,
              env.user
          ))
    sudo("chown {0} -R {1}".format(remote_user, remote_dir))


@task
@runs_once
def build_wheelhouse():
    command = (
        'pip wheel %(pip_args)s -w %(wheel_house)s '
        '--find-links %(wheel_house)s') % {
        'pip_args': _get_pip_install_args(),
        'wheel_house': BASE_WHEEL_DIR
    }

    # pylint: disable=E1129
    with cd(BASE_WHEEL_BASE_DIR):
        sudo(command)


@task
def update_requirement(deployment_params):
    command = (
        '%(pip_exc)s install -r %(reqfile)s --find-links '
        '%(wheel_house)s --no-index') % {
        'pip_exc': '{}/bin/pip'.format(deployment_params['virtualenv']),
        'reqfile': deployment_params['requirements'],
        'wheel_house': BASE_WHEEL_DIR,
    }
    # pylint: disable=E1129
    with cd(deployment_params['remote_dir']):
        sudo(command)


@task
def python_refresh(services):
    for service in services:
        with settings(warn_only=True):
            sta = sudo("supervisorctl status {}".format(service))
            if "STOPPED" in sta:
                continue
            sudo("supervisorctl restart {}".format(service))


@task
def status(services=SERVICES):
    for service in services:
        with settings(warn_only=True):
            sta = sudo("supervisorctl status {}".format(service))
            if "STOPPED" in sta:
                print(red(sta))
            else:
                print(green(sta))


def _do_deploy(app_id):
    deployment_params = DEPLOYMENT_PARAMS
    execute(virtualenv_init, deployment_params['virtualenv'])
    sync_args = [
        deployment_params['local_dir'],
        deployment_params['remote_dir'],
        deployment_params['remote_user'],
        deployment_params['remote_exclude']
    ]
    execute(common_rsync, *sync_args)
    execute(build_wheelhouse)
    execute(update_requirement, deployment_params)

    service_names = get_service_name_by_app_ids([app_id])
    execute(python_refresh, service_names)
    execute(status, service_names)


@task
def quick_deploy(app_ids):
    for app_id in app_ids:
        print green('\nquick deploy %s to %s\n' % (app_id, env.hosts))
        deployment_params = DEPLOYMENT_PARAMS
        execute(virtualenv_init, deployment_params['virtualenv'])
        sync_args = [
            deployment_params['local_dir'],
            deployment_params['remote_dir'],
            deployment_params['remote_user'],
            deployment_params['remote_exclude']
        ]
        execute(common_rsync, *sync_args)
    service_names = get_service_name_by_app_ids(app_ids)
    execute(python_refresh, service_names)
    execute(status, service_names)


def parse_app_ids(app_id):
    if app_id is None:
        app_ids = ALL_SERVICE_IDS
    else:
        if app_id not in ALL_SERVICE_IDS:
            raise ValueError('invalid app_id %s' % app_id)
        else:
            app_ids = [app_id, ]
    return app_ids


@task
def deploy(app_id=None, quick='True'):
    """
    1. create virtualenv if not exist
    2. sync code
    3. build wheel
    4. update requirements
    5. restart services
    """
    app_ids = parse_app_ids(app_id)

    if quick == 'True':
        return execute(quick_deploy, app_ids)
    else:
        for app_id in app_ids:
            print(green('\ndeploy %s to %s\n' % (app_id, env.hosts)))
            _do_deploy(app_id)
