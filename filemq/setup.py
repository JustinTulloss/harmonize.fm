from setuptools import setup, find_packages, Extension

setup(
    name='filemq',
    version="0.0.1",
    description='Message queue consumers to process uploaded files',
    install_requires=[
        "sqlalchemy>=0.5.3",
        "python-cjson>=1.0.3",
        "processing>=0.52",
        "amqplib>=0.6"
    ],
    #author='',
    #author_email='',
    #url='',
    packages=find_packages(exclude=['filemq.test']),
    test_suite='nose.collector',
    scripts=['fileprocessd']
)
