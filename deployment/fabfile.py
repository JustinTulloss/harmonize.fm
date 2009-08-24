config.project = 'harmonize'
config.repo = '/var/www/sites/repo/main'
config.fab_hosts = ['harmonize.fm']

def produce():
    "Push changes to live server"
    run("echo Pushing changes to production!")
    sudo('python $(repo)/deployment/produce.py')

def stage():
    "Push changes to staging server"
    run("echo Pushing changes to staging server")
    sudo('python $(repo)/deployment/stage.py')

def stage_pipeline():
    "Push changes to the file_pipeline only"
    sudo('python $(repo)/deployment/stage_pipeline.py')

def produce_pipeline():
    "Push changes to the live file pipeline from stage"
    sudo('python $(repo)/deployment/produce_pipeline.py')
