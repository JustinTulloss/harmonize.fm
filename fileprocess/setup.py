from setuptools import setup, find_packages, Extension

setup(
    name='fileprocess',
    version="0.0.1",
    description='Pipeline to process uploaded files',
    #author='',
    #author_email='',
    #url='',
    packages=find_packages(exclude=['fileprocess.test']),
    test_suite='nose.collector',
    scripts=['fileprocessd'],
    ext_modules = [
        Extension('fileprocess.actions.picard.util.astrcmp',
        ['fileprocess/actions/picard/util/astrcmp.cpp'])
    ]
)
