#!/usr/bin/env python3

from distutils.core import setup

from notspam import _VERSION

setup(
    name = 'notspam',
    version = _VERSION,
    description = 'Notmuch spam classification interface.',
    author = 'Jameson Graef Rollins',
    author_email = 'jrollins@finestructure.net',
    url = 'https://finestructure.net/notspam',

    py_modules = [
        'notspam',
        ],
    packages = [
        'notspam_classifiers',
        ],
    scripts = ['notspam'],
    package_data={'notspam': ['version.py']},

    requires = [
        'notmuch',
        ],
    )
