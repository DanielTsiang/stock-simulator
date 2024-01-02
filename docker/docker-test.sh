#!/usr/bin/env bash

echo "======= Running unit tests ======="
docker run --rm \
    --entrypoint python \
    -v $PWD/tests:/tests \
    stock-simulator:latest \
    -m unittest discover \
    -s ./tests \
    -p "test*.py"
