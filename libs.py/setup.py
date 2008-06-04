from setuptools import setup, find_packages

setup(
    name='libs.py',
    version="0.0.1",
    description='Libraries to support harmonize.fm',
    #author='',
    #author_email='',
    #url='',
    packages=find_packages(),
    py_modules=['S3', 'guid', 'mailer', 'mock', 'ecs', 'alert', 'df'],
    include_package_data=True,
    test_suite='nose.collector',
)
