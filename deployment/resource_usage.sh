#!/bin/bash

OUTFILE="/tmp/sut_resource_usage.csv"

# Print header
echo "timestamp,cpu_used,mem_used" > "$OUTFILE"

# Repeatedly capture CPU + Mem usage
while true; do
  # sar -u 1 1 -> capture CPU usage in a single snapshot over 1s
  CPU_USED=$(sar -u 1 1 | awk '/Average/ && /all/ { print 100 - $8 }')

  # sar -r 1 1 -> capture memory usage in a single snapshot over 1s
  MEM_USED=$(sar -r 1 1 | awk '/Average/ { print $4 }')

  # current time (epoch)
  TIMESTAMP=$(date +%s)

  # Append a single CSV line
  echo "${TIMESTAMP},${CPU_USED},${MEM_USED}" >> "$OUTFILE"

  sleep 5
done