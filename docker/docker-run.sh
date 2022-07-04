#!/usr/bin/env bash

docker run --name stock-simulator --rm -p 8000:8000 \
                                  --env DATABASE_URL \
                                  --env API_KEY \
                                  stock-simulator:latest
