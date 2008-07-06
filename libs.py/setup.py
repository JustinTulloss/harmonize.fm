from setuptools import setup, find_packages, Extension
ext = [
    Extension('picard_utils.util.astrcmp',['picard_utils/util/astrcmp.cpp'])
]
kwargs = {
    'name':'libs.py',
    'version':"0.0.1",
    'description':'Libraries to support harmonize.fm',
    #author:'',
    #author_email:'',
    #url:'',
    'install_requires': [
        "Pyrex>=0.9.8.4"
    ],
    'packages': find_packages(),
    'py_modules':['S3', 'guid', 'mailer', 'mock', 'ecs', 'alert', 'df', 'puid',
        'tag_compare', 'tag_utils'],
    'include_package_data':True,
    'test_suite': 'nose.collector',
    'ext_modules': ext
}
# This is all stolen from the sizer setup.py --JMT
try:
    from Pyrex.Distutils import build_ext
    
    """
    # Hack for Pyrex versions which define swig_sources
    # to only take two parameters.
    class my_build_ext(build_ext):
        def swig_sources(self, sources, ext = None):
            return build_ext.swig_sources(self, sources)
    """
            
    kwargs["cmdclass"] = {"build_ext": build_ext}
    ext.append(
        Extension("sizer.cpython.crules", 
                  ["sizer/cpython/crules.pyx"]))
except ImportError:
    import warnings
    print "Can't find Pyrex, so some types won't be counted accurately"

ext.append(
    Extension("sizer.cpython.utils",
              ["sizer/cpython/utils.c"]))

setup(**kwargs)
