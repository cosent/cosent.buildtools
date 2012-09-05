from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='cosent.buildtools',
      version=version,
      description="Release scripts",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python git buildout',
      author='Guido Stevens',
      author_email='guido.stevens@cosent.net',
      url='http://cosent.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
