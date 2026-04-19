#!/usr/bin/env bash
# Run the shell-based event-driven image annotation and retrieval demo.
set -euo pipefail

# Load broker and service modules.
source "shell_system/broker.sh"
source "shell_system/cli.sh"
source "shell_system/inference.sh"
source "shell_system/annotation.sh"
source "shell_system/embedding.sh"
source "shell_system/query.sh"

# Register services with the broker.
inference_start
annotation_start
embedding_start
query_start

# Subscribe to query completion events for logging.
query_logger() {
  local event=$1
  IFS='|' read -r event_id topic timestamp payload <<< "$event"
  local query
  query=$(payload_get "$payload" "query")
  local results
  results=$(payload_get "$payload" "results")
  echo
  echo "[RESULT] query='$query' results=$results"
}

broker_subscribe "query.completed" query_logger

# Clean previous storage and run the simulation.
rm -rf shell_system/storage
mkdir -p shell_system/storage/documents shell_system/storage/vectors
cli_run_simulation
broker_dispatch

# Show stored state after the demo.
echo
echo "Stored documents:"
find shell_system/storage/documents -type f -print -exec cat {} \;
echo
echo "Stored vectors:"
find shell_system/storage/vectors -type f -print -exec cat {} \;
