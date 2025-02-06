#!/bin/bash
HOST=$1
PORT=$2
if [ -z "$HOST" ] || [ -z "$PORT" ]; then
    echo "Usage: $0  "
    exit 1
fi
# Check if the specific port is open
nc -z -v -w2 $HOST $PORT 2>&1 | grep -q "succeeded"
if [ $? -eq 0 ]; then
    echo "CRITICAL: Port $PORT is open on $HOST"
    exit 2
else
    echo "OK: No open port $PORT detected on $HOST"
    exit 0
fi