#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = read("VERSION.txt").strip()
DESCRIPTION = "OMERO.openlink app"
AUTHOR = "sukunis"
MAINTAINER = "sukunis"
LICENSE = "AGPL-3.0"
HOMEPAGE = "https://github.com/sukunis/OMERO.openlink"


REQUIREMENTS = ["omero-web>=5.6.0"]


setup(name="omero-openlink",
      packages=find_packages(exclude=['ez_setup']),
      version=VERSION,
      description=DESCRIPTION,
      long_description=read('README.rst'),
      long_description_content_type="text/markdown",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Science/Research',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: JavaScript',
          'Programming Language :: Python :: 3',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Internet :: WWW/HTTP :: WSGI',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: Software Development :: Libraries :: '
          'Application Frameworks',
          'Topic :: Text Processing :: Markup :: HTML'
      ],  # Get strings from
          # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      author=AUTHOR,
      author_email='sinukesus@gmail.com',
      maintainer=MAINTAINER,
      license=LICENSE,
      url=HOMEPAGE,
      download_url="%s/archive/v%s.tar.gz" % (HOMEPAGE, VERSION),
      keywords=['OMERO.web', 'plugin','openlink'],
      install_requires=['omero-web>=5.6.0'],
      python_requires='>=3',
      include_package_data=True,
      zip_safe=False,
      )
