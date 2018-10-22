from setuptools import setup

setup(name='graphformation',
      version='0.1',
      description='A tiny implementation of Cloudformation/terraform-like system for learning purposes',
      url='http://github.com/graphformation',
      author='Stefan Savev',
      author_email='me@stefansavev.com',
      license='Apache',
      packages=['graphformation'],
      install_requires=[
            'toposort',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=True)