#!/usr/bin/env bash

echo "======= Running unit tests ======="
docker exec stock-simulator python3 -m unittest discover -s ./tests -p "test*"
