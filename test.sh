#!/bin/bash

LABEL="com.docker.compose.project"
VALUE="cashflow"

CONTAINER_ID=$(docker ps -q --filter "label=$LABEL=$VALUE")

echo "Container ID: $CONTAINER_ID"

# Command to run the tests
TEST_COMMAND="pytest -v --disable-warnings"

# Check if the container is already running
if [ $(docker ps -q -f name=$CONTAINER_ID) ]; then
    # If it is running, stop it
    echo "Stopping existing container..."
    docker stop $CONTAINER_ID
fi

# Remove the container if it exists
if [ $(docker ps -a -q -f name=$CONTAINER_ID) ]; then
    echo "Removing existing container..."
    docker rm $CONTAINER_ID
fi

# Run execute the tests
docker exec -it $CONTAINER_ID $TEST_COMMAND