# Package definition for the extras/display directory
#
# Copyright (C) 2018  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
from . import tmc4671


def load_config_prefix(config):
    return tmc4671.load_config(config)
