from setuptools import setup, find_packages
import os

version = '1.0.0.dev2'

setup(name='openprocurement.auth',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      url='https://github.com/openprocurement/openprocurement.auth',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Flask',
          'Flask-SQLAlchemy',
          'werkzeug',
          'Flask-OAuthlib'
      ],
      entry_points={
          'paste.app_factory': [
              'oauth_provider = openprocurement.auth.provider:make_oath_provider_app'
          ]
      },
      )
