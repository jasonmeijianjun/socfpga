#!/usr/bin/env python
# $Header: //acds/rel/17.0std/embedded/host_tools/altera/imagecat/alt_image_cat.py#1 $
#############################################################################
##  alt_image_cat.py
##
##  Altera Image Concatenation Utility
##
##  ALTERA LEGAL NOTICE
##
##  This script is  pursuant to the following license agreement
##  (BY VIEWING AND USING THIS SCRIPT, YOU AGREE TO THE
##  FOLLOWING): Copyright (c) 2015 Altera Corporation, San Jose,
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
__p4_file_header__ = "$Header: //acds/rel/17.0std/embedded/host_tools/altera/imagecat/alt_image_cat.py#1 $"
__version__ = "$Revision: #1 $"
__date__ = "$Date: 2017/01/22 $"

import argparse
import sys

from itertools import islice, cycle

class NargsRange(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if isinstance(nargs, tuple):
            self.minimum = nargs[0]
            self.maximum = nargs[1]

            if self.minimum == 0:
                argparse_nargs = '*'
            elif self.minimum > 0:
                argparse_nargs = '+'

            super(NargsRange, self).__init__(option_strings, dest, nargs=argparse_nargs, **kwargs)

            if not 0 <= self.minimum <= self.maximum:
                raise argparse.ArgumentError(self, "Invalid range '{}' requested for nargs".format(nargs))
        else:
            super(NargsRange, self).__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, args, values, option=None):
        if not self.minimum <= len(values) <= self.maximum:
            raise argparse.ArgumentError(self, "number of values provided ({}) does not fall between {} and {}".format(len(values), self.minimum, self.maximum))
        setattr(args, self.dest, values)


def main(argv):
    result = -1

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--output_image', help='File to write output image into', required=True)
        parser.add_argument('-a', '--alignment', help='Address alignment in KiB for output image', type=int, required=True)
        parser.add_argument('input_images', metavar='input_image', action=NargsRange, nargs=(1,4))

        args = parser.parse_args(argv)

        image_buffers = []
        for infile in args.input_images:
            image_buffer = open(infile, 'rb').read()
            # TODO: Check for size
            # TODO: Sanity check image type
            image_buffers.append(image_buffer)

        with open(args.output_image, 'wb') as outfile:
            for image_buffer in islice(cycle(image_buffers), 4):
                pad_length = (args.alignment * 1024) - len(image_buffer)
                outfile.write(image_buffer)
                outfile.write(b'\xFF' * pad_length)

        result = 0

    except Exception, err:
        print str(err)

    return result

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
