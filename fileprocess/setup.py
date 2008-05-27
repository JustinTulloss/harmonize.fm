from setuptools import setup, find_packages

setup(
    name='fileprocess',
    version="0.0.1",
    description='Pipeline to process uploaded files',
    #author='',
    #author_email='',
    #url='',
    packages=find_packages(exclude=['test']),
    test_suite='nose.collector',
    scripts=['fileprocess.py']
)
