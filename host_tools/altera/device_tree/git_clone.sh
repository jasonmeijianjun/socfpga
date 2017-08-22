#!/bin/bash -ex
git clone https://github.com/altera-opensource/sopc2dts.git
pushd sopc2dts && git checkout 9b3346002ac555f36b80b1bc56dad1cb86298234 -b release && popd
