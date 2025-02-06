#!/bin/bash

# Define the threshold for the warning and critical levels
WARNING_THRESHOLD=80
CRITICAL_THRESHOLD=90

# Get the current disk usage percentage for the root filesystem
USAGE=$(df / | tail -n 1 | awk '{print $5}' | sed 's/%//')

# Check for thresholds and format the output with performance data
if [ "$USAGE" -ge "$CRITICAL_THRESHOLD" ]; then
    echo "CRITICAL: Disk usage is at ${USAGE}% | diskusage=${USAGE}%;$WARNING_THRESHOLD;$CRITICAL_THRESHOLD;0;100"
    exit 2
elif [ "$USAGE" -ge "$WARNING_THRESHOLD" ]; then
    echo "WARNING: Disk usage is at ${USAGE}% | diskusage=${USAGE}%;$WARNING_THRESHOLD;$CRITICAL_THRESHOLD;0;100"
    exit 1
else
    echo "OK: Disk usage is at ${USAGE}% | diskusage=${USAGE}%;$WARNING_THRESHOLD;$CRITICAL_THRESHOLD;0;100"
    exit 0
fi
