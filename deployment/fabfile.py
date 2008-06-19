set(
    project = 'harmonize',
    repo = '/var/www/sites/repo/main',
    fab_hosts = ['harmonize.fm']
)

def produce():
    "Push changes to live server"
    sudo('python $(repo)/deployment/produce.py')

def stage():
    "Push changes to staging server"
    sudo('python $(repo)/deployment/stage.py')

def stage_pipeline():
    "Push changes to the file_pipeline only"
    sudo('python $(repo)/deployment/stage_pipeline.py')
