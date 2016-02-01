#!/usr/bin/env python

from distutils.core import setup

setup(name='CredentialCache',
      version      = '0.1',
      description  = 'Simple cache for authentication credentials',
      author       = 'Gabriele Mambrini',
      author_email = 'g.mambrini@gmail.com',
      packages     = ['credentialhelper' ],

      scripts      = [
          'scripts/credentialhelper',
          'scripts/credentialhelper-client',
          'scripts/credentialhelper-agent',
      ]
)
