from setuptools import setup, find_packages, Extension

setup(
    name='libs.py',
    version="0.0.1",
    description='Libraries to support harmonize.fm',
    #author='',
    #author_email='',
    #url='',
    packages=find_packages(),
    py_modules=['S3', 'guid', 'mailer', 'mock', 'ecs', 'alert', 'df', 'puid',
        'tag_compare', 'tag_utils'],
    include_package_data=True,
    test_suite='nose.collector',
    ext_modules = [
        Extension('picard_utils.util.astrcmp',['picard_utils/util/astrcmp.cpp'])
    ]
)
