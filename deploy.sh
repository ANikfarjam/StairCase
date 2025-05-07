#!/bin/bash

IMAGE_NAME="anikfarjam/staircase"
TAG="latest"
FULL_IMAGE="$IMAGE_NAME:$TAG"

echo "Building Docker image for linux/amd64..."
docker buildx build --platform linux/amd64 -t $FULL_IMAGE --load .

if [ $? -ne 0 ]; then
  echo "Build failed. Exiting."
  exit 1
fi

echo "Logging into Docker Hub..."
docker login

if [ $? -ne 0 ]; then
  echo "Login failed. Exiting."
  exit 1
fi

echo "Pushing image to Docker Hub with tag '$TAG'..."
docker push $FULL_IMAGE

if [ $? -ne 0 ]; then
  echo "Push failed. Exiting."
  exit 1
fi

echo "Running container using Agent and BackEnd .env files..."
docker run \
  --env-file Agent/.env \
  --env-file BackEnd/.env \
  -p 5001:5001 $FULL_IMAGE
