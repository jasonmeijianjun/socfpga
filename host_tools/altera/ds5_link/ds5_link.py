#!/usr/bin/env python
# Copyright 2014 Altera Corporation.
# $Header: //acds/rel/17.0std/embedded/host_tools/altera/ds5_link/ds5_link.py#2 $

"""
Simple utility that links DS-5 to the Altera-provided tools 

Usage:
    ds5_link.py [--absolute] [ds5_root]

    --absolute, -a: Force absolute path in .link file
    ds5_root: Override the detected DS-5 directory
"""

import os
import os.path
import sys
import argparse
import soceds_config

__version__ = "$Revision: #2 $"
__date__ = "$Date: 2017/02/02 $"
__copyright__ = "Copyright 2014 Altera Corporation."
__p4_file_header__ = "$Header: //acds/rel/17.0std/embedded/host_tools/altera/ds5_link/ds5_link.py#2 $"

def link_baremetal_toolchain(ds5_root, soceds_root, force_absolute=False):
    """Add a .link file to DS-5's installation that points to the
    Altera-provided baremetal toolchain, overwriting the previous .link file
    
    A relative path to the toolchain will be used if force_absolute=False and
    the DS-5 installation directory falls under the SoC EDS directory."""

    eclipse_path = os.path.join(ds5_root, "sw", "eclipse")
    linkfile_path = os.path.join(eclipse_path, "dropins",
                                 "altera_baremetal_gcc.link")

    toolchain_path = os.path.join(soceds_root,
                                  "host_tools", "mentor", "gnu", "arm")

    # Try to use relative path if DS-5 installed under SoCEDS root
    if not force_absolute:
        shared_prefix = os.path.commonprefix([ds5_root, soceds_root])
        if os.path.abspath(shared_prefix) == os.path.abspath(soceds_root):
            toolchain_path = os.path.relpath(toolchain_path, eclipse_path)

    # Even on Windows, Eclipse expects '/' instead of '\'
    toolchain_path = toolchain_path.replace("\\", "/")

    try:
        with open(linkfile_path, "w") as linkfile:
            print("{} => {}".format(linkfile_path, toolchain_path))
            linkfile.write("path={}".format(toolchain_path))
    except IOError as e:
        print("Unable to open/write file: {}".format(linkfile_path))
        return False

    return True

def link_cheatsheets(ds5_root, soceds_root, force_absolute=False):
    """Add a .link file to DS-5's installation that points to the
    Altera-provided cheatsheets, overwriting the previous .link file
    
    A relative path to the toolchain will be used if force_absolute=False and
    the DS-5 installation directory falls under the SoC EDS directory."""

    eclipse_path = os.path.join(ds5_root, "sw", "eclipse")
    linkfile_path = os.path.join(eclipse_path, "dropins", "altera_cheatsheets.lnk")

    toolchain_path = os.path.join(soceds_root,
                                  "host_tools", "altera", "cheatsheets")

    # Try to use relative path if DS-5 installed under SoCEDS root
    if not force_absolute:
        shared_prefix = os.path.commonprefix([ds5_root, soceds_root])
        if os.path.abspath(shared_prefix) == os.path.abspath(soceds_root):
            toolchain_path = os.path.relpath(toolchain_path, eclipse_path)

    # Even on Windows, Eclipse expects '/' instead of '\'
    toolchain_path = toolchain_path.replace("\\", "/")

    try:
        with open(linkfile_path, "w") as linkfile:
            print("{} => {}".format(linkfile_path, toolchain_path))
            linkfile.write("path={}".format(toolchain_path))
    except IOError as e:
        print("Unable to open/write file: {}".format(linkfile_path))
        return False

    return True



def main(command_line):
    """Script entry point"""
    parser = argparse.ArgumentParser(prog=command_line[0], description=
            """Link DS-5 Eclipse to the SoC EDS baremetal GCC toolchain.""")
    parser.add_argument("-a", "--absolute", action="store_true",
            dest="force_absolute", help=
            """Always use an absolute path for toolchain location""")
    parser.add_argument("ds5_root", nargs="?", help=
            """Override the detected DS-5 root directory""")
    args = parser.parse_args(command_line[1:])

    if args.ds5_root:
        ds5_root = os.path.abspath(args.ds5_root)
    else:
        ds5_root = soceds_config.get_ds5_root()

    if not ds5_root:
        print("Could not find DS-5 installation directory.")
        sys.exit(-1)

    soceds_root = soceds_config.get_soceds_root()
    if not soceds_root:
        print("Could not find SoC EDS installation directory.")
        sys.exit(-1)

    if (link_baremetal_toolchain(ds5_root, soceds_root, args.force_absolute) and
       link_cheatsheets(ds5_root, soceds_root, args.force_absolute)):
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == "__main__":
    main(sys.argv)

