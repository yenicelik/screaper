#!/usr/bin/env bash

docker build -t screaper -f ~/screaper/kubernetes/Dockerfile .
docker run -it -e DatabaseUrl=postgresql://postgres@docker.for.mac.host.internal:5432/scraper screaper
docker run -it --network=host -e DatabaseUrl=postgresql://postgres@0.0.0.0:5432/scraper screaper
