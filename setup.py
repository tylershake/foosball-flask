"""Foosball TrueSkill Setup

This script will install the foosball_trueskill package using distutils

"""

import distutils.core

distutils.core.setup(name='foosball_trueskill',
    version='0.1',
    description='Foosball TrueSkill Ranking Web Server',
    author='tshake',
    author_email='tshake@vt.edu',
    packages=['foosball_trueskill', 'foosball_trueskill.utils',
        'foosball_trueskill.tests'],
    package_data={'foosball_trueskill': ['utils/logging.conf']})
