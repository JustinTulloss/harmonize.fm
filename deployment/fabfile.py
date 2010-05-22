from fabric.api import env
from fabric.operations import sudo, run

env['project'] = 'harmonize'
env['repo'] = '/var/www/sites/repo/main'
env['hosts'] = ['harmonize.fm']

def produce():
    "Push changes to live server"
    run("echo Pushing changes to production!")
    sudo('python $(repo)s/deployment/produce.py' % env)

def stage():
    "Push changes to staging server"
    run("echo Pushing changes to staging server")
    sudo('python %(repo)s/deployment/stage.py' % env)

def stage_pipeline():
    "Push changes to the file_pipeline only"
    sudo('python %(repo)s/deployment/stage_pipeline.py' % env)

def produce_pipeline():
    "Push changes to the live file pipeline from stage"
    sudo('python %(repo)s/deployment/produce_pipeline.py' % env)
