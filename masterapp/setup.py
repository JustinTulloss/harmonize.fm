try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='masterapp',
    version="0.0.1",
    #description='',
    #author='',
    #author_email='',
    #url='',
    install_requires=["Pylons>=0.9.6.1", "sqlalchemy>=0.4beta3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'masterapp': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors = {'masterapp': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('public/**', 'ignore', None)]},
    entry_points="""
    [paste.app_factory]
    main = masterapp.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)