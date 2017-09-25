#!/bin/bash -ex
git clone https://github.com/altera-opensource/u-boot-socfpga.git
pushd u-boot-socfpga && git checkout -t -b socfpga_v2013.01.01 origin/socfpga_v2013.01.01 && popd
pushd u-boot-socfpga && git checkout 32c1d91bc0d10beca54c2dfc5b475d4ffeffc15a -b socfpga_v2013.01.01_release && popd
