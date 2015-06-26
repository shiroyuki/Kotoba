try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name         = 'Kotoba',
    version      = '3.1.1',
    description  = 'XML/JSON Reading Library with Level-3 CSS Selector',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'http://shiroyuki.com/work/projects-kotoba',
    packages     = ['kotoba']
)
