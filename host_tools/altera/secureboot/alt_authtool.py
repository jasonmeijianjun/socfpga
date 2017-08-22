#!/usr/bin/env python
# $Header: //acds/rel/17.0std/embedded/host_tools/altera/secureboot/alt_authtool.py#1 $
#############################################################################
##  authtool.py
##
##  Altera Authentication Signing Utility
##
##  ALTERA LEGAL NOTICE
##
##  This script is  pursuant to the following license agreement
##  (BY VIEWING AND USING THIS SCRIPT, YOU AGREE TO THE
##  FOLLOWING): Copyright (c) 2013-2014 Altera Corporation, San Jose,
##  California, USA.  Permission is hereby granted, free of
##  charge, to any person obtaining a copy of this software and
##  associated documentation files (the "Software"), to deal in
##  the Software without restriction, including without limitation
##  the rights to use, copy, modify, merge, publish, distribute,
##  sublicense, and/or sell copies of the Software, and to permit
##  persons to whom the Software is furnished to do so, subject to
##  the following conditions:
##
##  The above copyright notice and this permission notice shall be
##  included in all copies or substantial portions of the Software.
##
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
##  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
##  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
##  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
##  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
##  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
##  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
##  OTHER DEALINGS IN THE SOFTWARE.
##
##  This agreement shall be governed in all respects by the laws of
##  the State of California and by the laws of the United States of
##  America.
##
##
##  CONTACTING ALTERA
##
##  You can contact Altera through one of the following ways:
##
##  Mail:
##     Altera Corporation
##     Applications Department
##     101 Innovation Drive
##     San Jose, CA 95134
##
##  Altera Website:
##     www.altera.com
##
##  Online Support:
##     www.altera.com/mysupport
##
##  Troubleshooters Website:
##     www.altera.com/support/kdb/troubleshooter
##
##  Technical Support Hotline:
##     (800) 800-EPLD or (800) 800-3753
##        7:00 a.m. to 5:00 p.m. Pacific Time, M-F
##     (408) 544-7000
##        7:00 a.m. to 5:00 p.m. Pacific Time, M-F
##
##     From other locations, call (408) 544-7000 or your local
##     Altera distributor.
##
##  The mySupport web site allows you to submit technical service
##  requests and to monitor the status of all of your requests
##  online, regardless of whether they were submitted via the
##  mySupport web site or the Technical Support Hotline. In order to
##  use the mySupport web site, you must first register for an
##  Altera.com account on the mySupport web site.
##
##  The Troubleshooters web site provides interactive tools to
##  troubleshoot and solve common technical problems.

__copyright__ = "Copyright 2015 Altera Corporation."
__p4_file_header__ = "$Header: //acds/rel/17.0std/embedded/host_tools/altera/secureboot/alt_authtool.py#1 $"
__version__ = "$Revision: #1 $"
__date__ = "$Date: 2017/01/22 $"

import argparse
import os
import sys

basedir = os.path.dirname(__file__)
basedir = os.path.abspath(basedir)
sys.path.insert(0, os.path.join(basedir, "extlib", "pyasn1-0.1.7-py2.7.egg"))
sys.path.insert(0, os.path.join(basedir, "extlib", "pyasn1_modules-0.0.5-py2.7.egg"))

from authtool.command import register_hooks

def main(argv):
    result = -1

    try:
	## FB357820 pass in prog argument to update help menu usage name
        parser = argparse.ArgumentParser(prog='alt-secure-boot')
        subparsers = parser.add_subparsers(title='Available subcommands')

        for register_command in register_hooks:
            register_command(subparsers)

        args = parser.parse_args(argv)
        result = args.operation(args)

    except Exception, err:
        print str(err)

    return result

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
