#!/bin/bash
echo "Content-Type: text/text"
echo ""
echo "Rebuild started"
./build.sh 1>./build.log 2>./build-error.log &
