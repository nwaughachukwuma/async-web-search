#!/usr/bin/env bash

PORT=${PORT:-3131}
THREADS=${THREADS:-8}
WORKERS=${WORKERS:-4}

# Calculate default workers if WORKERS not set
echo "Starting server on port $PORT with $WORKERS workers and $THREADS threads per worker"

source .venv/bin/activate

exec granian --interface asgi src/index:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --runtime-threads "$THREADS" \
    --loop uvloop \
    --runtime-mode mt
