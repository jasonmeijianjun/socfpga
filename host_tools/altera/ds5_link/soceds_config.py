#!/usr/bin/env python
# Copyright 2014 Altera Corporation.
# $Header: //acds/rel/17.0std/embedded/host_tools/altera/ds5_link/soceds_config.py#1 $

"""
Utilities to query setup configuration for SoC EDS

This library can also be called directly from the command line. Configuration
is printed as <key>=<value> pairs, value blank if it could not be detected.

Usage:
    soceds_config.py [--get-ds5-root] [--get-soceds-root]
"""

import os
import os.path
import sys

__version__ = "$Revision: #1 $"
__date__ = "$Date: 2017/01/22 $"
__copyright__ = "Copyright 2014 Altera Corporation."
__p4_file_header__ = "$Header: //acds/rel/17.0std/embedded/host_tools/altera/ds5_link/soceds_config.py#1 $"

def _ds5_root_present(ds5_root):
    """Naively detect a valid DS-5 install root"""
    altera_configdb = os.path.join("sw", "debugger",
                                   "configdb", "Boards", "Altera")

    if isinstance(ds5_root, basestring):
        if os.path.isdir(os.path.join(ds5_root, altera_configdb)):
            return True

    return False

def _get_ds5_root_generic():
    """Naively find DS-5 installation"""

    ds5_root = os.path.join(os.environ["SOCEDS_DEST_ROOT"], "ds-5")

    if _ds5_root_present(ds5_root):
        return ds5_root
    else:
        return None

_get_ds5_root = _get_ds5_root_generic

if sys.platform.lower().startswith("win"):
    def _windows_64_hosting_32_bit():
        """Determine if script is running on 64-bit Windows with 32-bit
        programs, independently from the Python build architecture"""
        return "PROGRAMFILES(X86)" in os.environ

    def _get_ds5_root_windows():
        """Determine the location of DS-5 installation on Windows.

        Order of precedence:
            SOCEDS_D_R\ds-5 valid => use SOCEDS_D_R\ds-5
            Registry 64-bit DS-5 INSTALLDIR value
            Registry 32-bit DS-5 INSTALLDIR value
        """
        from winreg_wrapper import RegistryKey, RegistryKey32

        ds5_root = _get_ds5_root_generic()
        if _ds5_root_present(ds5_root):
            return ds5_root

        arm_key = RegistryKey("HKEY_LOCAL_MACHINE\\SOFTWARE\\ARM")
        subkeys = arm_key.subkeys

        if subkeys and len(subkeys):
            # Multiple DS-5 installations are theoretically possible, pick the
            # most recently installed one.
            ds5_key = max(subkeys.itervalues(), key=lambda k: k.last_modified)

            if "INSTALLDIR" in ds5_key.values:
                ds5_root = ds5_key.values["INSTALLDIR"]
                if _ds5_root_present(ds5_root):
                    return ds5_root

        if _windows_64_hosting_32_bit():
            arm_key = RegistryKey32("HKEY_LOCAL_MACHINE\\SOFTWARE\\ARM")
            subkeys = arm_key.subkeys

            if subkeys and len(subkeys):
                ds5_key = max(subkeys.itervalues(),
                              key=lambda k: k.last_modified)

                if "INSTALLDIR" in ds5_key.values:
                    ds5_root = ds5_key.values["INSTALLDIR"]
                    if _ds5_root_present(ds5_root):
                        return ds5_root

        return None

    _get_ds5_root = _get_ds5_root_windows
 
def get_ds5_root():
    """Return the fully-qualified location of the DS-5 installation"""

    ds5_root = _get_ds5_root()

    if ds5_root:
        return os.path.abspath(ds5_root)
    else:
        return None

def get_soceds_root():
    """Return the fully-qualified location of the SoC EDS installation"""
    soceds_root = os.environ["SOCEDS_DEST_ROOT"]

    if soceds_root and os.path.isdir(soceds_root):
        return os.path.abspath(soceds_root)
    else:
        return None


COMMAND_MAP = {
    "--get-ds5-root": ("DS5_ROOT", get_ds5_root),
    "--get-soceds-root": ("SOCEDS_ROOT", get_soceds_root),
}

def main(command_line):
    """Script entry point"""

    args = command_line[1:]
    config_values = []
    
    for command in args:
        if command in COMMAND_MAP:
            (name, function) = COMMAND_MAP[command]
            value = function()
            if not value:
                value = ""
            config_values.append("{n}={v}".format(n=name, v=value))
        else:
            print("Unrecognized command! ({})".format(command))
            sys.exit(-1)

    for output in config_values:
        print(output)

    sys.exit(0)

if __name__ == "__main__":
    main(sys.argv)

