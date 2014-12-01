from setuptools import setup, find_packages
import os

version = '1.0.0.dev8'

setup(name='openprocurement.auth',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
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
          # 'paste.app_factory': [
          #     'make_oath_provider_app = openprocurement.auth.provider:make_oath_provider_app'
          # ]
      },
      )
