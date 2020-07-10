#!/bin/bash

sudo docker system prune
sudo docker run -p 6379:6379 --name objrock-redis -e REDIS_PASSWORD=mypassword bitnami/redis:latest
