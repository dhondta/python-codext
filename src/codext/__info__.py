# -*- coding: UTF-8 -*-
"""Codext package information.

"""
import os
from datetime import datetime

__author__    = "Alexandre D'Hondt"
__copyright__ = "© 2019-{} A. D'Hondt".format(datetime.now().year)
__email__     = "alexandre.dhondt@gmail.com"
__license__   = "GPLv3 (https://www.gnu.org/licenses/gpl-3.0.fr.html)"
__source__    = "https://github.com/dhondta/python-codext"

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as f:
    __version__ = f.read().strip()

